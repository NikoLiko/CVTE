import src.setting as lib


if __name__ == "__main__":
    url_list, content_list = lib.check_env()
    lib.main(url_list, content_list)