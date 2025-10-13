// DlgInfoList.cpp : ʵ���ļ�
//

#include "pch.h"
#include "MfcTestLzdmAlg.h"
#include "DlgInfoList.h"
#include "afxdialogex.h"


// CDlgInfoList �Ի���

IMPLEMENT_DYNAMIC(CDlgInfoList, CDialogEx)

CDlgInfoList::CDlgInfoList(CWnd* pParent /*=NULL*/)
	: CDialogEx(CDlgInfoList::IDD, pParent)
{
	m_iCoutMax=200;

	InitializeCriticalSection(&m_csListInfo);
}

CDlgInfoList::~CDlgInfoList()
{
	DeleteCriticalSection(&m_csListInfo);
}

void CDlgInfoList::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}


BEGIN_MESSAGE_MAP(CDlgInfoList, CDialogEx)
	ON_WM_CTLCOLOR()
	ON_WM_DESTROY()
	ON_BN_CLICKED(IDB_LIST_CLEAR, &CDlgInfoList::OnBnClickedListClear)
END_MESSAGE_MAP()


// CDlgInfoList ��Ϣ�������


HBRUSH CDlgInfoList::OnCtlColor(CDC* pDC, CWnd* pWnd, UINT nCtlColor)
{
	HBRUSH hbr = CDialogEx::OnCtlColor(pDC, pWnd, nCtlColor);

	// TODO:  �ڴ˸��� DC ���κ�����
	pDC->SetBkMode(TRANSPARENT); //�������屳��Ϊ͸��
	hbr = (HBRUSH)::GetStockObject(WHITE_BRUSH);  // ���ñ���ɫ
	// TODO:  ���Ĭ�ϵĲ������軭�ʣ��򷵻���һ������
	return hbr;
}


void CDlgInfoList::OnDestroy()
{
	CDialogEx::OnDestroy();

	// TODO: �ڴ˴������Ϣ����������
}


BOOL CDlgInfoList::OnInitDialog()
{
	CDialogEx::OnInitDialog();


	//���ÿؼ�
	CRect rcDlg;
	GetClientRect(&rcDlg);

	GetDlgItem(IDC_LIST)->MoveWindow(rcDlg.left,rcDlg.top,rcDlg.Width()+2,rcDlg.Height()-20);
	GetDlgItem(IDB_LIST_CLEAR)->MoveWindow(rcDlg.left,rcDlg.bottom-20,rcDlg.Width()+2,20);

	// ������ʾ��
	m_ListBox.SubclassDlgItem(IDC_LIST,this);
	m_ListBox.SetHorizontalExtent(2000);	


	return TRUE;  // return TRUE unless you set the focus to a control
	// �쳣: OCX ����ҳӦ���� FALSE
}


BOOL CDlgInfoList::PreTranslateMessage(MSG* pMsg)
{
	if(pMsg -> message == WM_KEYDOWN)
	{
		if(pMsg -> wParam == VK_ESCAPE)
			return TRUE;
		if(pMsg -> wParam == VK_RETURN)
			return TRUE;
	}

	return CDialogEx::PreTranslateMessage(pMsg);
}


void CDlgInfoList::OnBnClickedListClear()
{
	m_ListBox.ResetContent();
}



void CDlgInfoList::DisplayInfo(CString str)
{
	EnterCriticalSection(&m_csListInfo);

	CListBox *myListBox=&m_ListBox;

	int	count;

	SYSTEMTIME st;
	GetLocalTime(&st);

	CString l_sCurTime;
	l_sCurTime.Format(_T("[%02d:%02d:%02d:%3d]"),st.wHour,st.wMinute,st.wSecond,st.wMilliseconds);
	//l_sCurTime.Format(_T("[%02d:%02d:%02d]"),st.wHour,st.wMinute,st.wSecond);
	
	CString l_sInfo=l_sCurTime+str;
	myListBox->AddString(l_sInfo);

	count=myListBox->GetCount();
	if (count>m_iCoutMax)
	{
		myListBox->DeleteString(0);
	}
	count=myListBox->GetCount();
	myListBox->SetCurSel(count-1);

	LeaveCriticalSection(&m_csListInfo);

}


void CDlgInfoList::SetCountMax(UINT n)
{
	if (n>1)
	{
		m_iCoutMax=n;
	}

}

//////////////////////////////////////////////////////////////////////////////
//���ܣ��ַ�����ָ���ָ������зָ�
/////////////////////////////////////////////////////////////////////////////
void  CDlgInfoList::ParseCString(CString source, CStringArray& dest, char division)
{

	dest.RemoveAll();
	int i;
	for (i = 0; i < source.GetLength(); i ++)
	{
		if (source.GetAt(i) == division)
		{
			dest.Add(source.Left(i)); //remove left
			for (int j = 0; j < (dest.GetSize() - 1); j ++)
			{
				dest[dest.GetSize()-1] = dest[dest.GetSize()-1].Right(dest[dest.GetSize()-1].GetLength()-dest[j].GetLength()-1);  //remove right
			}
		}
	}

	//The last string
	dest.Add(source.Left(i));
	for (int j = 0; j < (dest.GetSize() - 1); j ++)
	{
		dest[dest.GetSize()-1] = dest[dest.GetSize()-1].Right(dest[dest.GetSize()-1].GetLength()-dest[j].GetLength()-1);
	}

}

