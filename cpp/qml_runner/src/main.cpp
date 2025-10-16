#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QFileInfo>
#include <QDir>
#include <QUrl>
#include <QStringList>

static QString resolveMainQmlFromArgsOrDefaults(int argc, char* argv[]) {
  QString qmlPath;
  if (argc > 1) {
    qmlPath = QString::fromLocal8Bit(argv[1]);
    if (QFileInfo::exists(qmlPath)) return QFileInfo(qmlPath).absoluteFilePath();
  }

  // Try common locations relative to current dir and executable dir
  const QString appDir = QCoreApplication::applicationDirPath();
  const QStringList candidates = {
    QDir::current().filePath("app/ui/qml/main.qml"),
    QDir(appDir).filePath("../app/ui/qml/main.qml"),
    QDir(appDir).filePath("../../app/ui/qml/main.qml")
  };
  for (const auto& c : candidates) {
    if (QFileInfo::exists(c)) return QFileInfo(c).absoluteFilePath();
  }
  return QString();
}

int main(int argc, char *argv[])
{
  QGuiApplication app(argc, argv);

  const QString mainQml = resolveMainQmlFromArgsOrDefaults(argc, argv);
  if (mainQml.isEmpty()) {
    qWarning("main.qml not found. Pass path as argument or run from repo root.");
    qWarning("Example: qml_runner F:/Copper-Particle-Positioning-Grinding-System/app/ui/qml/main.qml");
    return -1;
  }

  QQmlApplicationEngine engine;
  const QUrl url = QUrl::fromLocalFile(mainQml);

  QObject::connect(&engine, &QQmlApplicationEngine::objectCreated, &app,
                   [url](QObject *obj, const QUrl &objUrl) {
                     if (!obj && url == objUrl) QCoreApplication::exit(-1);
                   }, Qt::QueuedConnection);

  engine.load(url);
  if (engine.rootObjects().isEmpty()) return -1;
  return app.exec();
}

