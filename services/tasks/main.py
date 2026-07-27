from app import create_app, settings

app = create_app()


if __name__ == "__main__":
    print(
        f"Starting {settings.SERVICE_NAME} service (version {settings.SERVICE_VERSION}) on {settings.HOST}:{settings.PORT} with debug={settings.DEBUG}"
    )

    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
