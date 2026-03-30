if __name__ == '__main__':
    import os
    import sys

    # poetry run nuitka main.py --include-package-data=tortoise --include-module=tortoise.backends.mysql --include-module=pydantic.validate_call_decorator --mode=standalone --include-package-data=tornado --include-module=tornado.iostream --include-module=tornado.gen --include-module=tornado.tcpserver --include-module=tornado.ioloop --include-package-data=fastapi --include-module=fastapi.responses --include-module=cryptography.fernet --include-package-data=cryptography --include-package-data=aiohttp --include-module=uvicorn --report=compilation-report.xml

    #root = os.path.dirname(os.environ.get("_PYI_ARCHIVE_FILE", os.getcwd()))

    root = os.getcwd()

    sys.path.append(root)
    import multiprocessing
    multiprocessing.set_start_method("spawn", force=True)
    multiprocessing.freeze_support()
    from battlenode import BattleNode
    bn = BattleNode(parent_dir=root)
    bn.run()