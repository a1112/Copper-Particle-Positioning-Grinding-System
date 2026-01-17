#include "frameless_helper.h"
#include <QCoreApplication>
#include <QGuiApplication>

#ifdef Q_OS_WIN
#include <windows.h>
#include <winuser.h>
#include <windowsx.h>
#endif

FramelessHelper::FramelessHelper(int titleBarHeight)
    : QAbstractNativeEventFilter()
    , m_titleBarHeight(titleBarHeight)
{
}

void FramelessHelper::setWindow(QWindow *window) {
    m_window = window;
}

void FramelessHelper::setTitleBarHeight(int height) {
    m_titleBarHeight = height;
}

FramelessHelper *FramelessHelper::install(QWindow *window, int titleBarHeight) {
    static FramelessHelper *instance = nullptr;

    if (!instance) {
        instance = new FramelessHelper(titleBarHeight);
        QCoreApplication::instance()->installNativeEventFilter(instance);
    } else {
        instance->setTitleBarHeight(titleBarHeight);
    }

    instance->setWindow(window);
    return instance;
}

#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
bool FramelessHelper::nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) {
#else
bool FramelessHelper::nativeEventFilter(const QByteArray &eventType, void *message, long *result) {
#endif

#ifdef Q_OS_WIN
    if (eventType == "windows_generic_MSG") {
        MSG *msg = static_cast<MSG *>(message);

        if (msg->message == WM_NCHITTEST && m_window) {
            if (!(m_window->flags() & Qt::FramelessWindowHint)) {
                return false;
            }
            HWND hwnd = reinterpret_cast<HWND>(m_window->winId());

            // 检查是否是我们的窗口
            if (msg->hwnd == hwnd) {
                return handleNCHITTEST(hwnd, msg->lParam, result);
            }
        }
    }
#else
    Q_UNUSED(eventType);
    Q_UNUSED(message);
    Q_UNUSED(result);
#endif

    return false;
}

#ifdef Q_OS_WIN
bool FramelessHelper::handleNCHITTEST(HWND hwnd, LPARAM lParam, qintptr *result) {
    // lParam 在 WM_NCHITTEST 中包含屏幕坐标
    // LOWORD(lParam) = x, HIWORD(lParam) = y
    const int x = GET_X_LPARAM(lParam);
    const int y = GET_Y_LPARAM(lParam);

    // 将屏幕坐标转换为客户区坐标
    POINT pt = { x, y };
    ScreenToClient(hwnd, &pt);

    // 检查鼠标是否在顶部拖拽区域
    if (pt.y >= 0 && pt.y < m_titleBarHeight) {
        *result = HTCAPTION;
        return true;
    }

    return false;
}
#endif
