#include <QCoreApplication>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQmlError>
#include <QTimer>
#include <QObject>
#include <QString>
#include <QtDebug>

class BackendStub : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)
    Q_PROPERTY(QString logs READ logs NOTIFY logsChanged)
    Q_PROPERTY(bool commConnected READ commConnected NOTIFY statusChanged)
    Q_PROPERTY(QString commLog READ commLog NOTIFY logsChanged)
    Q_PROPERTY(QString posText READ posText NOTIFY statusChanged)
    Q_PROPERTY(bool lockDoor READ lockDoor NOTIFY statusChanged)
    Q_PROPERTY(bool lockVacuum READ lockVacuum NOTIFY statusChanged)
    Q_PROPERTY(bool lockEStop READ lockEStop NOTIFY statusChanged)
    Q_PROPERTY(bool lockHomed READ lockHomed NOTIFY statusChanged)
    Q_PROPERTY(bool lockSpindle READ lockSpindle NOTIFY statusChanged)
    Q_PROPERTY(double targetX READ targetX NOTIFY statusChanged)
    Q_PROPERTY(double targetY READ targetY NOTIFY statusChanged)
    Q_PROPERTY(double targetTheta READ targetTheta NOTIFY statusChanged)
    Q_PROPERTY(double targetScore READ targetScore NOTIFY statusChanged)

public:
    explicit BackendStub(QObject *parent = nullptr)
        : QObject(parent),
          m_status(QStringLiteral("Idle")),
          m_logs(QStringLiteral("[stub] Backend initialized")),
          m_posText(QStringLiteral("X0.000 Y0.000 Z0.000 T0.000")),
          m_lockDoor(true),
          m_lockVacuum(true),
          m_lockEStop(false),
          m_lockHomed(true),
          m_lockSpindle(true),
          m_targetX(-1.0),
          m_targetY(-1.0),
          m_targetTheta(0.0),
          m_targetScore(0.0)
    {
        // Basic timer to simulate target movement and keep bindings active.
        auto timer = new QTimer(this);
        timer->setInterval(2500);
        connect(timer, &QTimer::timeout, this, &BackendStub::cycleDemoData);
        timer->start();
    }

    QString status() const { return m_status; }
    QString logs() const { return m_logs; }
    bool commConnected() const { return m_commConnected; }
    QString commLog() const { return m_commLog; }
    QString posText() const { return m_posText; }
    bool lockDoor() const { return m_lockDoor; }
    bool lockVacuum() const { return m_lockVacuum; }
    bool lockEStop() const { return m_lockEStop; }
    bool lockHomed() const { return m_lockHomed; }
    bool lockSpindle() const { return m_lockSpindle; }
    double targetX() const { return m_targetX; }
    double targetY() const { return m_targetY; }
    double targetTheta() const { return m_targetTheta; }
    double targetScore() const { return m_targetScore; }

    Q_INVOKABLE void setSpeed(double fast, double work) {
        appendLog(QStringLiteral("[stub] setSpeed fast=%1 work=%2").arg(fast).arg(work));
    }

    Q_INVOKABLE void jog(const QString &axis, int direction) {
        const double delta = 0.5 * (direction >= 0 ? 1.0 : -1.0);
        if (axis.compare(QStringLiteral("x"), Qt::CaseInsensitive) == 0) {
            m_targetX += delta;
        } else if (axis.compare(QStringLiteral("y"), Qt::CaseInsensitive) == 0) {
            m_targetY += delta;
        } else if (axis.compare(QStringLiteral("z"), Qt::CaseInsensitive) == 0) {
            m_virtualZ += delta;
        } else if (axis.compare(QStringLiteral("t"), Qt::CaseInsensitive) == 0) {
            m_targetTheta += delta;
        }
        updatePosText();
        emit statusChanged();
        appendLog(QStringLiteral("[stub] jog axis=%1 dir=%2").arg(axis).arg(direction));
    }

    Q_INVOKABLE void home() {
        m_targetX = 0.0;
        m_targetY = 0.0;
        m_targetTheta = 0.0;
        m_virtualZ = 0.0;
        updatePosText();
        appendLog(QStringLiteral("[stub] home() requested"));
        emit statusChanged();
    }

    Q_INVOKABLE void setWorkOrigin() {
        appendLog(QStringLiteral("[stub] setWorkOrigin() requested"));
    }

    Q_INVOKABLE void toggleComm(const QString &host, int port) {
        m_commConnected = !m_commConnected;
        appendLog(QStringLiteral("[stub] toggleComm host=%1 port=%2 -> %3")
                      .arg(host)
                      .arg(port)
                      .arg(m_commConnected ? QStringLiteral("connected")
                                           : QStringLiteral("disconnected")));
        emit statusChanged();
    }

    Q_INVOKABLE void refresh() {
        appendLog(QStringLiteral("[stub] refresh()"));
        emit statusChanged();
    }

signals:
    void statusChanged();
    void logsChanged();

private:
    void cycleDemoData() {
        // Simple demo oscillation to make visuals react inside Qt Creator previews.
        m_targetScore = (m_targetScore >= 0.9) ? 0.1 : (m_targetScore + 0.2);
        m_targetX = (m_targetX >= 100.0) ? -100.0 : (m_targetX + 20.0);
        m_targetY = (m_targetY >= 80.0) ? -80.0 : (m_targetY + 16.0);
        m_lockDoor = !m_lockDoor;
        m_lockVacuum = !m_lockVacuum;
        emit statusChanged();
    }

    void updatePosText() {
        m_posText = QStringLiteral("X%1 Y%2 Z%3 T%4")
                        .arg(m_targetX, 0, 'f', 3)
                        .arg(m_targetY, 0, 'f', 3)
                        .arg(m_virtualZ, 0, 'f', 3)
                        .arg(m_targetTheta, 0, 'f', 3);
    }

    void appendLog(const QString &line) {
        m_logs.append(QStringLiteral("\n") + line);
        m_commLog.append(QStringLiteral("\n") + line);
        emit logsChanged();
    }

    QString m_status;
    QString m_logs;
    QString m_commLog;
    QString m_posText;
    bool m_commConnected = false;
    bool m_lockDoor;
    bool m_lockVacuum;
    bool m_lockEStop;
    bool m_lockHomed;
    bool m_lockSpindle;
    double m_targetX;
    double m_targetY;
    double m_targetTheta;
    double m_targetScore;
    double m_virtualZ = 0.0;
};

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

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCoreApplication::setOrganizationName(QStringLiteral("CopperSystem"));
    QCoreApplication::setOrganizationDomain(QStringLiteral("example.local"));
    QCoreApplication::setApplicationName(QStringLiteral("Copper UI (C++ Stub)"));

    QQmlApplicationEngine engine;

    BackendStub backend;
    SettingsStub settings;
    HighlighterStub highlighter;

    engine.rootContext()->setContextProperty(QStringLiteral("backend"), &backend);
    engine.rootContext()->setContextProperty(QStringLiteral("settings"), &settings);
    engine.rootContext()->setContextProperty(QStringLiteral("pyHighlighter"), &highlighter);

    const QUrl url(QStringLiteral("qrc:/qml/main.qml"));
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        [](const QList<QQmlError> &errors) {
            for (const auto &err : errors) {
                qWarning() << err;
            }
            QCoreApplication::exit(-1);
        },
        Qt::QueuedConnection);

    engine.load(url);
    if (engine.rootObjects().isEmpty()) {
        return -1;
    }

    return app.exec();
}

#include "main.moc"
