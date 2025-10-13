
// MfcTestLzdmAlgDlg.cpp: 实现文件
//

#include "pch.h"
#include "framework.h"
#include "MfcTestLzdmAlg.h"
#include "MfcTestLzdmAlgDlg.h"
#include "afxdialogex.h"



#ifdef _DEBUG
#define new DEBUG_NEW
#endif



// CMfcTestLzdmAlgDlg 对话框



CMfcTestLzdmAlgDlg::CMfcTestLzdmAlgDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_MFCTESTLZDMALG_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CMfcTestLzdmAlgDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CMfcTestLzdmAlgDlg, CDialogEx)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BUTTON1, &CMfcTestLzdmAlgDlg::OnBnClickedButton1)
	ON_BN_CLICKED(IDC_BUTTON2, &CMfcTestLzdmAlgDlg::OnBnClickedButton2)
	ON_BN_CLICKED(IDC_BUTTON3, &CMfcTestLzdmAlgDlg::OnBnClickedButton3)
	ON_BN_CLICKED(IDC_BUTTON5, &CMfcTestLzdmAlgDlg::OnBnClickedButton5)
	ON_BN_CLICKED(IDC_BUTTON6, &CMfcTestLzdmAlgDlg::OnBnClickedButton6)
	ON_BN_CLICKED(IDC_BUTTON4, &CMfcTestLzdmAlgDlg::OnBnClickedButton4)
	ON_WM_TIMER()
END_MESSAGE_MAP()


// CMfcTestLzdmAlgDlg 消息处理程序

BOOL CMfcTestLzdmAlgDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 设置此对话框的图标。  当应用程序主窗口不是对话框时，框架将自动
	//  执行此操作
	SetIcon(m_hIcon, TRUE);			// 设置大图标
	SetIcon(m_hIcon, FALSE);		// 设置小图标

	// TODO: 在此添加额外的初始化代码



 	SetTimer(1, 100, FALSE);

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。  对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void CMfcTestLzdmAlgDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 用于绘制的设备上下文

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 使图标在工作区矩形中居中
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 绘制图标
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR CMfcTestLzdmAlgDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}


void  CMfcTestLzdmAlgDlg::DoEvents()
{
	MSG msg;
	// Process existing messages in the application's message queue.
	// When the queue is empty, do clean up and return.
	while (::PeekMessage(&msg, NULL, 0, 0, PM_NOREMOVE))
	{

		if (!AfxGetThread()->PumpMessage())
			return;
	}
}

void CMfcTestLzdmAlgDlg::DelayT(DWORD time)
{
	if (time <= 0)
	{
		return;
	}

	DWORD t = ::GetTickCount();

	while (::GetTickCount() - t < time)
	{
		DoEvents();

	}

}






void CMfcTestLzdmAlgDlg::InitUI()
{

	InitView();

	//信息提示栏
	CRect rc;
	GetDlgItem(IDS_ROI_LIST)->GetWindowRect(&rc);
	ScreenToClient(rc);
	m_pDlgInfoList = NULL;
	m_pDlgInfoList = new CDlgInfoList();
	m_pDlgInfoList->Create(IDD_DLGINFOLIST, this);
	m_pDlgInfoList->ShowWindow(1);
	::SetWindowPos(m_pDlgInfoList->m_hWnd, HWND_TOP, rc.left, rc.top, rc.Width(), rc.Height(), SWP_SHOWWINDOW/*SWP_NOSIZE*/);

	return;
}


void CMfcTestLzdmAlgDlg::InitView()
{
	//图像编辑栏
	CRect rsView;
	GetDlgItem(IDS_ROI_IMG)->GetWindowRect(&rsView);
	ScreenToClient(rsView);
	rsView.top += 0; rsView.bottom += 0;
	rsView.left += 0; rsView.right += 0;


	int nRow, nCol;

	//视窗数量
	int iNumView = 0;
	switch (/*m_sSetViewPara.iMode*/0)
	{
	case 0:iNumView = 1;
		nRow = 1; nCol = 1;
		break;
	case 1:iNumView = 2;
		nRow = 1; nCol = 2;
		break;
	case 2:iNumView = 4;
		nRow = 2; nCol = 2;
		break;
	case 3:iNumView = 6;
		nRow = 2; nCol = 3;
		break;
	default:
		iNumView = 1;
		nRow = 1; nCol = 1;
	}

	//分割窗口区域
	CRect* pRect2 = new CRect[nRow * nCol];;
	if (!RegionSegmentByMatrix(rsView, nRow, nCol, pRect2))
	{
		delete[] pRect2;
		pRect2 = NULL;
		return;
	}

	for (int i = 0; i < nRow * nCol; i++)
	{
		pRect2[i].left += 3; pRect2[i].right += -3;
		pRect2[i].top += 3; pRect2[i].bottom += -3;

		if ((1 == nRow) && (2 == nCol))
		{
			pRect2[i].bottom = pRect2[i].top + pRect2[i].Height() * 0.5;

			pRect2[i].OffsetRect(0, 0.25 * rsView.Height());
		}

		if ((2 == nRow) && (3 == nCol))
		{
			int iBotton = pRect2[i].bottom;
			pRect2[i].bottom = iBotton - 0.2 * pRect2[i].Height();
		}
	}


	//清除窗口
	for (int i = 0; i < m_pListDlgImageWindow.size(); i++)
	{
		m_pListDlgImageWindow[i]->DestroyWindow();
		delete m_pListDlgImageWindow[i];
		m_pListDlgImageWindow[i] = NULL;
	}
	m_pListDlgImageWindow.clear();


	//生成窗口
	for (int i = 0; i < iNumView; i++)
	{
		CDlgImageWindow* pAClass;
		pAClass = new CDlgImageWindow;
		pAClass->Create(IDD_DLGIMAGEWINDOW, this);
		pAClass->MoveWindow(pRect2[i]);
		pAClass->ShowWindow(1);
		pAClass->InitHWindow();
		m_pListDlgImageWindow.push_back(pAClass);
	}


	delete[] pRect2;

	return;
}


bool CMfcTestLzdmAlgDlg::RegionSegmentByMatrix(CRect Rect1, int nRow, int nCol, CRect* pRect2)
{
	//首先判断一些异常情况，长宽设置异常，矩阵设置异常
	int nWidth = Rect1.Width();
	int nHeight = Rect1.Height();

	if ((nWidth < 2) || (nHeight < 2))
	{
		return false;
	}
	if ((nRow < 1) || (nCol < 1))
	{
		return false;
	}

	int nSegWidth = nWidth / nCol;
	int nSegHeight = nHeight / nRow;

	CRect* rect = new CRect[nRow * nCol];
	for (int i = 0; i < nRow; i++)
	{
		for (int j = 0; j < nCol; j++)
		{
			rect[i * nCol + j].left = Rect1.left + j * nSegWidth;
			rect[i * nCol + j].right = Rect1.left + (j + 1) * nSegWidth;
			rect[i * nCol + j].top = Rect1.top + i * nSegHeight;
			rect[i * nCol + j].bottom = Rect1.top + (i + 1) * nSegHeight;
			pRect2[i * nCol + j] = rect[i * nCol + j];
		}
	}
	delete[] rect;
	return true;
}



void CMfcTestLzdmAlgDlg::OnBnClickedButton1()
{
	// TODO: 在此添加控件通知处理程序代码

	CFileDialog fileDialog(TRUE, _T("png"), NULL, OFN_FILEMUSTEXIST | OFN_HIDEREADONLY,
		_T("PNG Files (*.png)|*.png||"));

	// 弹出文件对话框
	if (fileDialog.DoModal() != IDOK)
	{
		return;
	}

	// 获取用户选择的文件路径
	CString filePath = fileDialog.GetPathName();


	std::string  strFullPath = std::string(CT2A(filePath));

	std::string strFullPathNameRemoveSuffix ;

	const std::string suffix = "_IMG_Texture_8Bit.png";
	strFullPathNameRemoveSuffix= strFullPath.substr(0, strFullPath.size() - suffix.size());


	m_pListDlgImageWindow[0]->ClearWindow();

	s_Image3dS imgT;
	CHVisionAdvX lHVisionAdvXObj;
	if (lHVisionAdvXObj.ReadImage3DX(imgT, strFullPathNameRemoveSuffix.c_str()))
	{

		CString sInfo;
		sInfo.Format(_T("自动：读取图像失败--%s \n"), strFullPathNameRemoveSuffix.c_str());
		LogX(sInfo);

		return;
	}

	mImgT = imgT.DeepCopy();

	//HObject  ho_Image;
	//ReadImage(&ho_Image,HTuple( filePath));
	m_pListDlgImageWindow[0]->DispImage(imgT.Gray.Clone());

	

}


void CMfcTestLzdmAlgDlg::OnBnClickedButton2()
{
	// TODO: 在此添加控件通知处理程序代码
	CString sInfo;

	CPreProcess lProObj;

	m_sPreProcess3DSPara.fRoiZMin = 1600.000;
	m_sPreProcess3DSPara.fRoiZMax = 1850.000;
	m_sPreProcess3DSPara.fRoiXMin = -500.000;
	m_sPreProcess3DSPara.fRoiXMax = 400.000;
	m_sPreProcess3DSPara.fRoiYMin = -300.000;
	m_sPreProcess3DSPara.fRoiYMax = 500.000;
	m_sPreProcess3DSPara.fThSeg0Dis = 30.000;
	m_sPreProcess3DSPara.iThSeg0NumPtsMin = 5000;
	m_sPreProcess3DSPara.iThSeg0NumPtsMax = 5000000;
	m_sPreProcess3DSPara.fThSeg0DiameterMin = 300.000;
	m_sPreProcess3DSPara.fThSeg0DiameterMax = 3000.000;

	s_PreProcess3DSResultPara sPreProcessRts;
	s_Rtnf sRts =lProObj.OnPreProcess(mImgT, m_sPreProcess3DSPara, sPreProcessRts);
	
	if (sRts.iCode != 0)
	{

		sInfo.Format(_T("自动：预处理图像失败--%s \n"), sRts.strInfo.c_str());
		LogX(sInfo);

		return;
	}



	m_sPreProcess3DSResultPara = sPreProcessRts.DeepCopy();

	m_pListDlgImageWindow[0]->ClearWindow();
	m_pListDlgImageWindow[0]->DispImage(sPreProcessRts.sImage3dPro.Gray.Clone());


}

void CMfcTestLzdmAlgDlg::LogX(CString str)
{
         m_pDlgInfoList->DisplayInfo(str);

		 m_Log.Log(str);

}


void CMfcTestLzdmAlgDlg::OnBnClickedButton3()
{
	// TODO: 在此添加控件通知处理程序代码
	CString sInfo;


	m_sDefectPlateBPara.fThNZAbsVal = 0.800;
	m_sDefectPlateBPara.fThNXAbsVal = 0.200;
	m_sDefectPlateBPara.fThNYAbsVal = 0.200;
	m_sDefectPlateBPara.fThGrayVal = 50.000;
	m_sDefectPlateBPara.fQgOffsetL = 25.000;
	m_sDefectPlateBPara.fQgOffsetR = 25.000;
	m_sDefectPlateBPara.fQgOffsetU = 25.000;
	m_sDefectPlateBPara.fQgOffsetD = 25.000;
	m_sDefectPlateBPara.fThBulgeLower = 1.500;
	m_sDefectPlateBPara.fThBulgeHiger = 3.000;
	m_sDefectPlateBPara.fQgHOrg = 18.000;
	m_sDefectPlateBPara.fQgExCol = 15.000;
	m_sDefectPlateBPara.fQgExRow = 9.000;
	m_sDefectPlateBPara.fQgThOffset = 3.000;
	m_sDefectPlateBPara.fConnectionDis = 50.000;


	s_DefectPlateBRtsPara sDefectPlateBRtsPara ;
	CPlateB lCPlateBObj;
	s_Rtnf sRts = lCPlateBObj.OnDetect(m_sPreProcess3DSResultPara.sImage3dPro, m_sDefectPlateBPara,  sDefectPlateBRtsPara);
	//lock(m_LockRts)  //图像数据加锁  如能确保此刻数据不被其他线程访问 可取消加锁及深拷贝
	//{
		m_sDefectPlateBRtsPara = sDefectPlateBRtsPara.DeepCopy();
	//}

	if (sRts.iCode != 0)
	{
		sInfo.Format(_T("自动：缺陷检测失败--%s \n"), sRts.strInfo.c_str());
		LogX(sInfo);
		return;
	}

    m_pListDlgImageWindow[0]->ClearWindow();
	m_pListDlgImageWindow[0]->DispImage(sDefectPlateBRtsPara.ImageZ1ZeroReal.Clone());
	
	m_pListDlgImageWindow[0]->ClearObj();
	m_pListDlgImageWindow[0]->DispObj(sDefectPlateBRtsPara.RectPartLzC.Clone(), "red");
	m_pListDlgImageWindow[0]->DispObj(sDefectPlateBRtsPara.RectPartLzL.Clone(), "red");
	m_pListDlgImageWindow[0]->DispObj(sDefectPlateBRtsPara.RectPartLzU.Clone(), "red");
	m_pListDlgImageWindow[0]->DispObj(sDefectPlateBRtsPara.RectPartLzD.Clone(), "red");
	m_pListDlgImageWindow[0]->DispObj(sDefectPlateBRtsPara.RectPartLzR.Clone(), "red");


	sInfo.Format(_T("自动：缺陷检测 耗时=%d ms \n"), (int)(sDefectPlateBRtsPara.time * 1000));
	LogX(sInfo);

}

HObject m_hoPtsQgNotSafeList ;
HObject m_hoCrossList ;
HObject m_hoArrowList ;
int m_indexPath = 0;

void CMfcTestLzdmAlgDlg::OnBnClickedButton5()
{
	// TODO: 在此添加控件通知处理程序代码


	CString sInfo;

	m_sJggyPara.fDjDiamiter = 80.000;
	m_sJggyPara.fJgLzUpOffset = 2.000;
	m_sJggyPara.fJgDpUpOffset = 1.500;
	m_sJggyPara.iModeJgPPZStepMode = 1;
	m_sJggyPara.fJgPPZStepFix = 2.000;
	m_sJggyPara.fJgPPZStepK = 0.300;
	m_sJggyPara.fJgPPZStepB = 1.500;
	m_sJggyPara.iModeJgPPYStepMode = 0;
	m_sJggyPara.fJgPPYStepFix = 50.000;
	m_sJggyPara.fJgPPYStepK = 0.750;
	m_sJggyPara.iModeJgPPSort = 0;
	m_sJggyPara.fQgSafeDis = 50.000;
	m_sJggyPara.fJgTdZUp = 20.000;

	s_LzppRtsPara sLzppRtsPara ;

	CPlateB lPlateBObj;
	s_Rtnf sRts = lPlateBObj.OnLzPP(m_sJggyPara, m_sDefectPlateBRtsPara,  sLzppRtsPara);
	//lock(m_LockRts)  //图像数据加锁  如能确保此刻数据不被其他线程访问 可取消加锁及深拷贝
	//{
		m_sLzppRtsPara = sLzppRtsPara.DeepCopy();
	//}

	if (sRts.iCode != 0)
	{
		sInfo.Format(_T("自动：路径规划失败--%s \n"), sRts.strInfo.c_str());
		LogX(sInfo);
		
		return;
	}

	HObject GrayZ;
   Compose2(m_sPreProcess3DSResultPara.sImage3dPro.Gray, m_sPreProcess3DSResultPara.sImage3dPro.Z, &GrayZ);

	HObject GrayXYZ;
	Compose4(m_sPreProcess3DSResultPara.sImage3dPro.Gray,
		m_sPreProcess3DSResultPara.sImage3dPro.X,
		m_sPreProcess3DSResultPara.sImage3dPro.Y,
		m_sPreProcess3DSResultPara.sImage3dPro.Z, &GrayXYZ);


	m_pListDlgImageWindow[0]->ClearWindow();
	m_pListDlgImageWindow[0]->DispImage(GrayXYZ.Clone());
	m_pListDlgImageWindow[0]->ClearObj();
	m_pListDlgImageWindow[0]->DispObj(sLzppRtsPara.RegionMxAllList.Clone(), "red");

	sInfo.Format(_T("自动：路径规划 耗时=%d \n"), (int)(sLzppRtsPara.time * 1000));
	LogX(sInfo);


	for (int i = 0; i < sLzppRtsPara.sListPPts.size(); i++)
	{
		s_PPts As = sLzppRtsPara.sListPPts[i];

		sInfo.Format(_T("自动：路径点%d--def-xyz=[%d,  %.1f,  %.1f,  %.1f]--图像坐标[%.1f , %.1f]--避让气缸索引=[%s] \n"), i, As.iDef, As.fX, As.fY, As.fZ, As.fCol, As.fRow, As.strQgNotSafe.c_str());
		LogX(sInfo);

	}

	//图形--加工点和避让点
	HTuple hRowAll =HTuple();
	HTuple hColAll = HTuple();

	HTuple hRowQg =  HTuple();
	HTuple hColQg =  HTuple();

	for (int i = 0; i < m_sLzppRtsPara.sListPPts.size(); i++)
	{
		s_PPts As = m_sLzppRtsPara.sListPPts[i];

		hRowAll.Append(As.fRow);
		hColAll.Append(As.fCol);

		if (As.strQgNotSafe.size() != 0)
		{
			hRowQg.Append(As.fRow);
			hColQg.Append(As.fCol);
		}

	}

	//加工点
	GenEmptyObj(&m_hoCrossList);

	HObject ho_Cross ;
	GenCrossContourXld(&ho_Cross, hRowAll, hColAll, 21, 0);
	ConcatObj(m_hoCrossList, ho_Cross, &m_hoCrossList);


	//避让点
	GenEmptyObj(&m_hoPtsQgNotSafeList);
	HObject ho_PtsQgNotSafe ;
	HTuple hv_Newtuple = HTuple();

	TupleGenConst(HTuple(hRowQg.TupleLength()), 5, &hv_Newtuple);
	GenCircle(&ho_PtsQgNotSafe, hRowQg, hColQg, hv_Newtuple);
	ConcatObj(m_hoPtsQgNotSafeList, ho_PtsQgNotSafe, &m_hoPtsQgNotSafeList);

	//箭头
	m_indexPath = 0;
	GenEmptyObj(&m_hoArrowList);
	for (int i = 0; i < m_sLzppRtsPara.sListPPts.size() - 1; i++)
	{
		s_PPts As = m_sLzppRtsPara.sListPPts[i];
		s_PPts Bs = m_sLzppRtsPara.sListPPts[i + 1];

		HObject ho_Arrow;
		GenEmptyObj(&ho_Arrow);
	
		CHVisionAdvX lHVisionAdvXObj;
		lHVisionAdvXObj.gen_arrow_contour_xld(&ho_Arrow, As.fRow, As.fCol, Bs.fRow, Bs.fCol, 5, 3);
		ConcatObj(m_hoArrowList, ho_Arrow, &m_hoArrowList);

	}


	m_pListDlgImageWindow[0]->DispObj(ho_Cross.Clone(), "green");
	m_pListDlgImageWindow[0]->DispObj(ho_PtsQgNotSafe.Clone(), "red");



}

void CMfcTestLzdmAlgDlg::OnBnClickedButton4()
{
	// TODO: 在此添加控件通知处理程序代码

	HObject GrayZ;
	Compose2(m_sPreProcess3DSResultPara.sImage3dPro.Gray, m_sPreProcess3DSResultPara.sImage3dPro.Z, &GrayZ);

	HObject GrayXYZ;
	Compose4(m_sPreProcess3DSResultPara.sImage3dPro.Gray,
		m_sPreProcess3DSResultPara.sImage3dPro.X,
		m_sPreProcess3DSResultPara.sImage3dPro.Y,
		m_sPreProcess3DSResultPara.sImage3dPro.Z, &GrayXYZ);


	m_pListDlgImageWindow[0]->ClearWindow();

	int iNum = m_hoArrowList.CountObj();
	for (int i = 0; i < iNum; i++)
	{
		HObject ho_Arrow;
		SelectObj(m_hoArrowList, &ho_Arrow, i + 1);

		m_pListDlgImageWindow[0]->DispImage(GrayXYZ.Clone());

		m_pListDlgImageWindow[0]->ClearObj();
		m_pListDlgImageWindow[0]->DispObj(m_sLzppRtsPara.RegionMxAllList.Clone(), "blue");
		m_pListDlgImageWindow[0]->DispObj(m_hoCrossList.Clone(), "green");
		m_pListDlgImageWindow[0]->DispObj(m_hoPtsQgNotSafeList.Clone(), "red");

		m_pListDlgImageWindow[0]->SetLineWidthX(3);
		m_pListDlgImageWindow[0]->DispObj(ho_Arrow.Clone(), "red");
		m_pListDlgImageWindow[0]->SetLineWidthX(2);

		DelayT(500);
	}

}


void CMfcTestLzdmAlgDlg::OnBnClickedButton6()
{
	// TODO: 在此添加控件通知处理程序代码

	HObject GrayZ;
	Compose2(m_sPreProcess3DSResultPara.sImage3dPro.Gray, m_sPreProcess3DSResultPara.sImage3dPro.Z, &GrayZ);

	HObject GrayXYZ;
	Compose4(m_sPreProcess3DSResultPara.sImage3dPro.Gray,
		m_sPreProcess3DSResultPara.sImage3dPro.X,
		m_sPreProcess3DSResultPara.sImage3dPro.Y,
		m_sPreProcess3DSResultPara.sImage3dPro.Z, &GrayXYZ);


	m_pListDlgImageWindow[0]->ClearWindow();

	int iNum = m_hoArrowList.CountObj();
	if (m_indexPath < iNum)
	{
		HObject ho_Arrow;
	SelectObj(m_hoArrowList, &ho_Arrow, m_indexPath + 1);

	m_pListDlgImageWindow[0]->DispImage(GrayXYZ.Clone());

	m_pListDlgImageWindow[0]->ClearObj();
	m_pListDlgImageWindow[0]->DispObj(m_sLzppRtsPara.RegionMxAllList.Clone(), "blue");
	m_pListDlgImageWindow[0]->DispObj(m_hoCrossList.Clone(), "green");
	m_pListDlgImageWindow[0]->DispObj(m_hoPtsQgNotSafeList.Clone(), "red");

	m_pListDlgImageWindow[0]->SetLineWidthX(5);
	m_pListDlgImageWindow[0]->DispObj(ho_Arrow.Clone(), "red");
	m_pListDlgImageWindow[0]->SetLineWidthX(2);

		m_indexPath++;
	}
	else
	{
		m_indexPath = 0;
	}



}



void CMfcTestLzdmAlgDlg::OnTimer(UINT_PTR nIDEvent)
{
	// TODO: 在此添加消息处理程序代码和/或调用默认值

	if (1 == nIDEvent)
	{
		InitUI();

		KillTimer(1);
	}

	CDialogEx::OnTimer(nIDEvent);
}
