from cleo.application import Application

from flick.cmd import serve


def main():
    application = Application()
    application.add(serve.ServeCommand())
    application.run()


if __name__ == "__main__":
    main()
