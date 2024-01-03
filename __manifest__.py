{
    'name': "Logistics",  # 模块的名称
    'summary': "Logistics Management System",  # 简单描述
    'category': 'Productivity',  # 用于按照兴趣领域组织模块
    'description': """ An open source, simple and user-friendly logistics information management system """,  # 长描述，通常放在三个引号中，Python中使用三个引号来界定多行文本
    'License': 'LGPL-3',  # 默认值为LGPL-3。这一标识符用于模块对外使用的证书。其它可用的证书有AGPL-3、Odoo自有证书v1.0（多用于付费应用）以及其它OSI核准的证书。
    # 这是该模块所直接依赖的模块技术名称列表。如果你的模块不依赖于任何其它插件模块，那么应至少添加一个base模块。别忘记包含这个模块所引用的XML ID、视图或模块的定义模型。那样可确保它们以正确的顺序进行加载，避免难以调试的错误。
    'depends': ['base', 'mail'],

    'data': [
        'security/logistics_security.xml',
        'security/ir.model.access.csv',
        'views/waybill.xml',
        'views/city.xml',
        'views/goods.xml',
        'views/package.xml',
        'views/rate.xml',
        'views/receiver.xml',
        'views/shipper.xml',
        'views/menu.xml'
    ],  # 这是在模块安装或升级时需加载数据文件的相对路径列表。这些路径相对于模块的根目录。通常，这些是XML和CSV文件，但也可以使用YAML格式的数据文件
    'demo': [],  # 这是加载演示数据文件的相对路径列表。仅在创建数据库时启用了Demo Data标记时才会进行加载。
    'qweb': [],
    'installable': True,  # 若为True（默认值），表示该模块可以进行安装。
    'application': True,  # 如果为True，模块作为应用列出。通常这用于一个功能区的中心模块。
    'auto_install': False,  # 若为True，表示这是一个*胶水*模块，在它所有的依赖模块安装后会被自动安装。
    'author': "HSpring",  # 是一个作者姓名的字符串。如果有多个作者的话，一般使用逗号来进行分隔，但注意它仍应是一个字符串，而非Python列表
    'website': "https://gardenengineer.club/",  # 这个 URL 可供人们访问来了解模块或作者的更多信息
    'version': '16.0.1.0',  # 这是该模块的版本号。可供Odoo应用商店用于检测已安装模块的新版本。如果版本号没有以Odoo目标版本号（如14.0）开头，会进行自动添加。但是，如果你显式的声明Odoo目标版本号信息量会更充足，比如用14.0.1.0.0或14.0.1.0来替代1.0.0或1.0。
}
