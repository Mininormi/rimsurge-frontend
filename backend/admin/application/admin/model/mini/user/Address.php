<?php

namespace app\admin\model\mini\user;

use think\Model;


class Address extends Model
{

    

    

    // 表名
    protected $table = 'mini_user_address';
    
    // 自动写入时间戳字段
    protected $autoWriteTimestamp = 'integer';

    // 定义时间戳字段名
    protected $createTime = 'createtime';
    protected $updateTime = 'updatetime';
    protected $deleteTime = false;

    // 追加属性
    protected $append = [
        'address_type_text'
    ];
    

    
    public function getAddressTypeList()
    {
        return ['shipping' => __('Shipping'), 'billing' => __('Billing')];
    }


    public function getAddressTypeTextAttr($value, $data)
    {
        $value = $value ?: ($data['address_type'] ?? '');
        $list = $this->getAddressTypeList();
        return $list[$value] ?? '';
    }




}
