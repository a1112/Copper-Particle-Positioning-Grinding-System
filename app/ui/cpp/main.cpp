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
    HighlighterStub highlighter;
    LocalizationStub i18n;

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




