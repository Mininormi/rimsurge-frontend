# Bug修复说明文档

本文档记录项目中需要手动修复的第三方依赖问题。

## 修复记录

### 修复 #1: FastAdmin 插件本地上传网络错误问题

**问题描述：**
- 日期：2025-12-12
- 问题：在 FastAdmin 后台本地上传插件时，出现"网络错误!"异常，导致插件无法安装
- 错误信息：`{code: 0, msg: "网络错误!", data: "", url: "", wait: 3}`

**问题原因：**
`Service::local()` 方法在安装插件时会调用 `Service::valid()` 进行远程验证，该方法会向 FastAdmin API (`https://api.fastadmin.net/addon/valid`) 发送请求。当网络请求失败（无法连接、超时或API不可用）时，会抛出"网络错误"异常，导致本地上传失败。

**修复位置：**
文件：`backend/admin/vendor/fastadminnet/fastadmin-addons/src/addons/Service.php`
方法：`Service::valid()` (第248-280行)

**修复内容：**
在 `Service::valid()` 方法中添加了网络错误的容错处理：

1. 如果允许未知来源且在调试模式下，跳过远程验证
2. 如果网络验证失败：
   - 在调试模式下，允许继续安装
   - 即使不在调试模式下，如果是本地上传（有文件MD5），也允许继续安装

**修复代码：**
public static function valid($params = [])
{
    // 如果允许未知来源且在调试模式下，跳过远程验证
    if (isset($params['unknownsources']) && $params['unknownsources'] && config('app_debug')) {
        return true;
    }
    
    try {
        $json = self::sendRequest('/addon/valid', $params, 'POST');
        if ($json && isset($json['code'])) {
            if ($json['code']) {
                return true;
            } else {
                throw new Exception($json['msg'] ?? "Invalid addon package");
            }
        } else {
            throw new Exception("Unknown data format");
        }
    } catch (Exception $e) {
        // 如果是网络错误，在调试模式下允许继续安装（本地上传不需要远程验证）
        $errorMessage = $e->getMessage();
        if (stripos($errorMessage, __('Network error')) !== false || stripos($errorMessage, 'Network error') !== false) {
            // 在调试模式下，网络错误时允许继续安装
            if (config('app_debug')) {
                return true;
            }
            // 即使不在调试模式下，如果是本地上传（有文件MD5），也允许继续
            // 因为本地上传不应该依赖远程API验证
            if (isset($params['md5']) && !empty($params['md5'])) {
                return true;
            }
        }
        throw $e;
    }
}**注意事项：**
1. ⚠️ **重要**：由于 `vendor` 目录被 `.gitignore` 忽略，此修复不会自动同步到Git仓库
2. ⚠️ **重要**：如果运行 `composer install` 或 `composer update`，此修复会被覆盖，需要重新应用
3. ⚠️ **重要**：部署到新环境时，需要手动应用此修复

**重新应用修复的方法：**
1. 打开文件：`backend/admin/vendor/fastadminnet/fastadmin-addons/src/addons/Service.php`
2. 找到 `Service::valid()` 方法（约第248行）
3. 按照上述修复代码进行修改

**验证修复：**
1. 访问 FastAdmin 后台插件管理页面
2. 点击"本地安装"按钮
3. 选择一个插件文件（.zip 或 .fastaddon）进行上传
4. 应该能够成功安装，不再出现"网络错误"异常

---

## 如何维护此文档

- 每次修复第三方依赖问题时，请在此文档中添加新的修复记录
- 包含问题描述、原因、修复位置、修复代码和注意事项
- 确保其他开发者能够根据此文档重新应用修复
