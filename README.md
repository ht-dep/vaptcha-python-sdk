# vaptcha-python-sdk

### Step1.环境准备

- Vaptcha Python SDK 兼容python2.7+，如有较低版本用户，[请联系vaptcha技术支持](https://wpa.qq.com/msgrd?v=3&uin=1828005327&site=qq&menu=yes)。目前提供基于WSGI服务器的DEMO。


- 要使用Vaptcha Python SDK，你需要一个Vaptcha账号、一个验证单元以及一对VID和Key。请在Vaptcha验证管理后台查看。

### Step2.SDK获取和安装

- 使用`git`命令获取

  ```shell
  git clone https://github.com/vaptcha/vaptcha-python-sdk.git
  ```

  [github地址](https://github.com/vaptcha/vaptcha-python-sdk)手动下载获取

- 进入`/vaptcha-python-sdk`目录，安装`vaptchasdk`

  > 也许你需要`sudo`命令，或者管理员身份下运行该命令

  ```shell
   python setup.py install
  ```

- 引入`vaptcha`

  ```Python
  from vaptchasdk import vaptcha
  ```

- 配置`vid`和`key`并创建`vaptcha`对象

  ```
  vid, key = 'xxxxxxxxxxxxxxxxxxxxxxxx', 'xxxxxxxxxxxxxxxxxxxxxxxx'
  _vaptcha = vaptcha(vid, key)
  ```

- 运行demo

  > demo中的vid和key使用的是vaptcha官方为demo免费提供的，缺少一些限制，可能存在安全隐患。在实际生产环境中，我们建议你登陆[vaptcha管理后台](https://www.vaptcha.com/manage)，在验证管理中添加对应的验证单元，并把domain参数设置为实际环境中的域名。

  进入`/vaptcha-python-sdk/demo`目录，运行如下命令,并在http://localhost:4396中查看

  ```shell
  python server.py
  ```

### Step3.SDK接口说明

​	SDK提供以下三个接口：

- `get_challenge(scene_id='')`

  > 获取流水号接口，用于获取vid和challenge

  参数：

  ​	`scene_id`:场景id，请在vaptcha管理后台查看,类型：字符串，选填

  返回值：json字符串

  example：

  ```Python
  result = _vaptcha.get_challenge()
  ```


- `downtime(data)`

  > 宕机模式接口，用户宕机模式的相关验证，仅用于和vaptcha客户端sdk交互

  参数：

  ​	`data`：由vapthca客户端sdk回传，类型：字符串

  返回值：json字符串

  example：

  ```Python
  result = _vaptcha.downtime(data)
  ```


- `validate(challenge,token,scene_id='')`

  > 二次验证接口，用于与vaptcha服务器的二次验证。

  参数：

  ​	`challenge`：由用户客户端回传，类型：字符串

  ​	`token`：由用户客户端回传，类型：字符串

  ​      `scene_id`：由用户配置，与`get_challenge`接口的`scene_id`一致，类型：字符串，选填

  返回值：bool类型

  example:

  ```python
  result = _vaptcha.validate(challenge, token)
  ```