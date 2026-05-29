if __name__ == "__main__":
    from checkout import create_app
    create_app().run(debug=True, port=8080)
