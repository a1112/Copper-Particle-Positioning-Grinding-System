#pragma once


// CDlgInfoList �Ի���

class CDlgInfoList : public CDialogEx
{
	DECLARE_DYNAMIC(CDlgInfoList)

public:
	CDlgInfoList(CWnd* pParent = NULL);   // ��׼���캯��
	virtual ~CDlgInfoList();

// �Ի�������
	enum { IDD = IDD_DLGINFOLIST };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV ֧��

	DECLARE_MESSAGE_MAP()
public:
	afx_msg HBRUSH OnCtlColor(CDC* pDC, CWnd* pWnd, UINT nCtlColor);
	afx_msg void OnDestroy();
	virtual BOOL OnInitDialog();
	virtual BOOL PreTranslateMessage(MSG* pMsg);


	//������ʾ
	CListBox m_ListBox;

	

	afx_msg void OnBnClickedListClear();
	void DisplayInfo(CString str);
	void SetCountMax(UINT n);

	void ParseCString(CString source, CStringArray& dest, char division);

	UINT m_iCoutMax;

	CRITICAL_SECTION m_csListInfo;
};
