#pragma once


// CDlgInfoList 对话框

class CDlgInfoList : public CDialogEx
{
	DECLARE_DYNAMIC(CDlgInfoList)

public:
	CDlgInfoList(CWnd* pParent = NULL);   // 标准构造函数
	virtual ~CDlgInfoList();

// 对话框数据
	enum { IDD = IDD_DLGINFOLIST };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

	DECLARE_MESSAGE_MAP()
public:
	afx_msg HBRUSH OnCtlColor(CDC* pDC, CWnd* pWnd, UINT nCtlColor);
	afx_msg void OnDestroy();
	virtual BOOL OnInitDialog();
	virtual BOOL PreTranslateMessage(MSG* pMsg);


	//滚动提示
	CListBox m_ListBox;

	

	afx_msg void OnBnClickedListClear();
	void DisplayInfo(CString str);
	void SetCountMax(UINT n);

	void ParseCString(CString source, CStringArray& dest, char division);

	UINT m_iCoutMax;

	CRITICAL_SECTION m_csListInfo;
};
