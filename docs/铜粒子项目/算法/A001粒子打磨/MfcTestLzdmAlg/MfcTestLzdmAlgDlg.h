
// MfcTestLzdmAlgDlg.h: 头文件
//

#pragma once

#include "DlgImageWindow.h"
#include "CPreProcess.h"
#include "CPlateB.h"
#include "CHVisionAdvX.h"
#include "DlgInfoList.h"

#include "LogX.h"

// CMfcTestLzdmAlgDlg 对话框
class CMfcTestLzdmAlgDlg : public CDialogEx
{
// 构造
public:
	CMfcTestLzdmAlgDlg(CWnd* pParent = nullptr);	// 标准构造函数

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_MFCTESTLZDMALG_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 支持


// 实现
protected:
	HICON m_hIcon;

	// 生成的消息映射函数
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()


	afx_msg void OnBnClickedButton1();
	afx_msg void OnBnClickedButton2();
	afx_msg void OnBnClickedButton3();
	afx_msg void OnBnClickedButton5();

	void InitUI();

	void InitView();

	void LogX(CString str);

private:
	bool RegionSegmentByMatrix(CRect Rect1, int nRow, int nCol, CRect* pRect2);
public:
	
	void DelayT(DWORD time);
	void  DoEvents();

	//属性
	vector<CDlgImageWindow*> m_pListDlgImageWindow;
	CDlgInfoList* m_pDlgInfoList;
	CLogX m_Log;

	s_Image3dS mImgT;
	s_PreProcess3DSPara m_sPreProcess3DSPara;
	s_PreProcess3DSResultPara m_sPreProcess3DSResultPara;

	s_DefectPlateBPara m_sDefectPlateBPara;
	s_DefectPlateBRtsPara m_sDefectPlateBRtsPara;

	s_JggyPara m_sJggyPara;
	s_LzppRtsPara m_sLzppRtsPara;


	afx_msg void OnBnClickedButton6();
	afx_msg void OnBnClickedButton4();
	afx_msg void OnTimer(UINT_PTR nIDEvent);
};
