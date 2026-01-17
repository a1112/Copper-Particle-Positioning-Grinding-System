#ifndef FRAMELESS_HELPER_H
#define FRAMELESS_HELPER_H

#include <QAbstractNativeEventFilter>
#include <QWindow>

#ifdef Q_OS_WIN
#include <windows.h>
#endif

/**
 * @brief 无边框窗口Windows Aero Snap支持
 *
 * 原理：拦截WM_NCHITTEST消息，当鼠标在顶部区域时返回HTCAPTION，
 * 让Windows认为用户正在拖拽标题栏，从而触发Aero Snap。
 */
class FramelessHelper : public QAbstractNativeEventFilter {

public:
    explicit FramelessHelper(int titleBarHeight = 40);
    ~FramelessHelper() override = default;

    void setWindow(QWindow *window);
    void setTitleBarHeight(int height);

    // 安装到应用程序
    static FramelessHelper *install(QWindow *window, int titleBarHeight = 40);

protected:
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    bool nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) override;
#else
    bool nativeEventFilter(const QByteArray &eventType, void *message, long *result) override;
#endif

private:
    int m_titleBarHeight;
    QWindow *m_window = nullptr;

#ifdef Q_OS_WIN
    bool handleNCHITTEST(HWND hwnd, LPARAM lParam, qintptr *result);
#endif
};

#endif // FRAMELESS_HELPER_H
