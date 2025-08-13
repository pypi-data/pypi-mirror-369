# usdk/cli.py
import asyncclick as click
import logging
import os
import json
from getpass import getpass
from yunhu_usdk import yunhu_usdk
import aiohttp
# 基本配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('usdk.log'),
        logging.StreamHandler(),
    ],
    force=True
)
@click.group()  # 定义一个命令组
async def cli():
    pass

@cli.command()  # 定义 "init" 子命令
async def init():
    usdk = yunhu_usdk()
    logging.info("正在初始化项目.....")
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            data = f.read()
            if not data:
                config = {}
            else:
                config = json.loads(data)
        if config:
            if config.get("email", ""):
                logging.warning(f"当前目录已经存在配置文件(已检测到{config['email']}的登录)，如果继续将替换掉原有配置文件。")
            else:
                logging.warning(f"当前目录已经存在配置文件，如果继续将替换掉原有配置文件。")
            logging.info("如果程序可以正常运行，我们建议您不要更换token")
            choice = input("是否要继续？(Y/n)")
            while True:
                if choice == "N" or choice == 'n':
                    logging.info("退出初始化成功")
                    return
                elif choice == "y" or choice == "Y":
                    break
                else:
                    logging.error("未知选项，请重新输入")
                    choice = input("是否要继续？(Y/n)")
                    continue
    logging.info("正在进行项目初始化...")
    login_choice = input("""(1)邮箱+密码登录
(2)直接填入token
(3)手机号登录
(0)暂时不登陆
请选择登陆方式：""")
    if login_choice == "0":
        with open("config.json", "w", encoding="utf-8") as f:
            data = {
                "token": "",
                "user_id": "",
            }
            f.write(json.dumps(data))
        logging.info("项目初始化完成")
        logging.info("接下来，请前往config.json手动填写token和user_id，以便接口调用")
    elif login_choice == "1":
        email = input("请输入邮箱：")
        password = getpass("请输入密码：")
        login_data = await usdk.Login.Email(email, password)
        if login_data['code'] == 1:
            token = login_data['data']['token']
            user_data = await usdk.Person.Info(token)
            with open("config.json", "w", encoding="utf-8") as f:
                data = {
                    "token": token,
                    "email": email,
                    "user_id": user_data['data']['id']
                }
                f.write(json.dumps(data))
            logging.info("项目初始化完成")
        else:
            logging.error("项目初始化失败，请重试！")
    elif login_choice == "2":
        token = input("请输入token：")
        user_id = input("请输入用户id：")
        with open("config.json", "w", encoding="utf-8") as f:
            data = {
                "token": token,
                "user_id": user_id
            }
            f.write(json.dumps(data))
        logging.info("项目初始化完成")
    elif login_choice == "3":
        phone = input("请输入手机号：")
        data = await usdk.Person.Captcha()
        verify_id = data['data']['id']
        verify_image = data['data']['b64s']
        async with aiohttp.ClientSession() as session:
            async with session.post("https://uapis.cn/api/v1/image/frombase64", json={
                "imageData": verify_image
            }) as res:
                data = await res.json()
                print(data)
                if data['code'] != 200:
                    logging.error("图片验证码获取失败，请重试！")
                    return 
                print(f"请使用浏览器访问链接：{data['image_url']}，并且把图片中的字符输入到下方:")
                code = input("请输入图片中的字符：")
                get_code_data = await usdk.Person.GetCode(phone, verify_id, code, "windows")
                if get_code_data['code'] != 1:
                    logging.error("获取验证码失败，请重试！")
                    return
                print("验证码已经发送到您的手机，请耐心等待，并且输入验证码")
                phone_verify_code = input("请输入验证码：")
                login_data = await usdk.Person.PhoneLogin(phone, phone_verify_code, "windows")
                if login_data['code'] != 1:
                    logging.error("手机号登录失败，请重试！")
                    return
                token = login_data['data']['token']
                if login_data['code'] == 1:
                    token = login_data['data']['token']
                    user_data = await usdk.Person.Info(token)
                    with open("config.json", "w", encoding="utf-8") as f:
                        data = {
                            "token": token,
                            "email": phone,
                            "user_id": user_data['data']['id']
                        }
                        f.write(json.dumps(data))
                    logging.info("项目初始化完成")
                else:
                    logging.error("项目初始化失败，请重试！")
if __name__ == "__main__":
    cli(_anyio_backend="asyncio")