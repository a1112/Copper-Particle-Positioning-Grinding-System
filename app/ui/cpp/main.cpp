#include <QCoreApplication>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQmlError>
#include <QIcon>
#include <QObject>
#include <QString>
#include <QtDebug>
#include <QSettings>
#include <QVariantList>
#include <QVariantMap>


class SettingsStub : public QObject {
    Q_OBJECT
    Q_PROPERTY(int apiPort READ apiPort WRITE setApiPort NOTIFY apiPortChanged)
    Q_PROPERTY(QString apiHost READ apiHost WRITE setApiHost NOTIFY apiHostChanged)
    Q_PROPERTY(bool debugEnabled READ debugEnabled CONSTANT)
    Q_PROPERTY(QString savedText READ savedText WRITE setSavedText NOTIFY savedTextChanged)

public:
    explicit SettingsStub(QObject *parent = nullptr)
        : QObject(parent)
    {}

    int apiPort() const { return m_apiPort; }
    void setApiPort(int port) {
        if (m_apiPort == port) {
            return;
        }
        m_apiPort = port;
        emit apiPortChanged();
    }

    QString apiHost() const { return m_apiHost; }
    void setApiHost(const QString &host) {
        if (m_apiHost == host) {
            return;
        }
        m_apiHost = host;
        emit apiHostChanged();
    }

    bool debugEnabled() const { return false; }

    QString savedText() const { return m_savedText; }
    void setSavedText(const QString &text) {
        if (m_savedText == text) {
            return;
        }
        m_savedText = text;
        emit savedTextChanged();
    }

    Q_INVOKABLE void save() const {}
    Q_INVOKABLE void saveAndRestart() const {}
    Q_INVOKABLE void clearController() {}

signals:
    void apiPortChanged();
    void apiHostChanged();
    void savedTextChanged();

private:
    int m_apiPort = 8010;
    QString m_apiHost = QStringLiteral("127.0.0.1");
    QString m_savedText;
};

class HighlighterStub : public QObject {
    Q_OBJECT

public:
    explicit HighlighterStub(QObject *parent = nullptr)
        : QObject(parent)
    {}

    Q_INVOKABLE void attach(QObject *document) {
        Q_UNUSED(document);
    }
};

class LocalizationStub : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString currentLanguage READ currentLanguage WRITE setCurrentLanguage NOTIFY languageChanged)
    Q_PROPERTY(QVariantList availableLanguages READ availableLanguages CONSTANT)

public:
    explicit LocalizationStub(QObject *parent = nullptr)
        : QObject(parent)
    {
        m_availableLanguages = {
            QVariantMap{{QStringLiteral("code"), QStringLiteral("zh_CN")}, {QStringLiteral("label"), QStringLiteral("\u7b80\u4f53\u4e2d\u6587")}},
            QVariantMap{{QStringLiteral("code"), QStringLiteral("en_US")}, {QStringLiteral("label"), QStringLiteral("English")}},
            QVariantMap{{QStringLiteral("code"), QStringLiteral("ja_JP")}, {QStringLiteral("label"), QStringLiteral("\u65e5\u672c\u8a9e")}},
        };

        QSettings settings;
        const QString stored = settings.value(QStringLiteral("language"), QStringLiteral("zh_CN")).toString();
        m_language = stored.isEmpty() ? QStringLiteral("zh_CN") : stored;
    }

    QString currentLanguage() const { return m_language; }

    void setCurrentLanguage(const QString &code) {
        const QString normalized = code.isEmpty() ? QStringLiteral("zh_CN") : code;
        if (normalized == m_language) {
            return;
        }
        m_language = normalized;
        QSettings settings;
        settings.setValue(QStringLiteral("language"), m_language);
        emit languageChanged();
    }

    QVariantList availableLanguages() const { return m_availableLanguages; }

    Q_INVOKABLE QString displayName(const QString &code) const {
        for (const QVariant &entry : m_availableLanguages) {
            const QVariantMap map = entry.toMap();
            if (map.value(QStringLiteral("code")).toString() == code) {
                return map.value(QStringLiteral("label")).toString();
            }
        }
        return code;
    }

signals:
    void languageChanged();

private:
    QString m_language;
    QVariantList m_availableLanguages;
};

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCoreApplication::setOrganizationName(QStringLiteral("CopperSystem"));
    QCoreApplication::setOrganizationDomain(QStringLiteral("example.local"));
    QCoreApplication::setApplicationName(QStringLiteral("Copper UI (C++ Stub)"));
    QGuiApplication::setWindowIcon(QIcon(QStringLiteral(":/resource/app.ico")));

    QQmlApplicationEngine engine;

    SettingsStub settings;
    HighlighterStub highlighter;
    LocalizationStub i18n;

    engine.rootContext()->setContextProperty(QStringLiteral("settings"), &settings);
    engine.rootContext()->setContextProperty(QStringLiteral("pyHighlighter"), &highlighter);
    engine.rootContext()->setContextProperty(QStringLiteral("i18n"), &i18n);

    const QUrl url(QStringLiteral("qrc:/qml/main.qml"));
    engine.load(url);
    if (engine.rootObjects().isEmpty()) {
        qWarning() << "Failed to load QML entry point:" << url;
        return -1;
    }

    return app.exec();
}

#include "main.moc"


