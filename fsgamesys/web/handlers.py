from fstd.webapp import WebApp

app = WebApp()


@app.route("/")
def test():
    print("hello")
    return "Heisann"
