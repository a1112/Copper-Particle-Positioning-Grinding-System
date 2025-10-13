#pragma once

#include "halconcpp.h"
#include <vector>
using namespace HalconCpp;

// 相机设备信息
struct s_CameraInfo
{
	std::string SN = "";                      //序列号
	std::string sDeviceUserID = "";           //使用名
	std::string sModelName = "";              //型号
	std::string IpAddr = "";                  //IP
};

//驱动信息
struct s_DevicesInfo
{
	int iNum;
	std::string sDevSource;
	s_CameraInfo sCameraInfo[20];
};

//3D结构光相机图像
class s_Image3dS
{
public:
	HObject Gray;
	HObject X;
	HObject Y;
	HObject Z;
	HObject NX;
	HObject NY;
	HObject NZ;
	HTuple ObjectModel3D;
	long ID; //图像ID

	s_Image3dS()
	{
		GenEmptyObj(&Gray);
		GenEmptyObj(&X);
		GenEmptyObj(&Y);
		GenEmptyObj(&Z);
		GenEmptyObj(&NX);
		GenEmptyObj(&NY);
		GenEmptyObj(&NZ);
		ObjectModel3D.Clear();
		ID = -1;
	}


	void Clear()
	{

		Gray.Clear();
		X.Clear();
		Y.Clear();
		Z.Clear();
		NX.Clear();
		NY.Clear();
		NZ.Clear();

		if (ObjectModel3D.Length() > 0)
		{
			ClearObjectModel3d(ObjectModel3D);
			ObjectModel3D.Clear();
		}
		ID = -1;
	}


	s_Image3dS DeepCopy()
	{
		s_Image3dS As;

		//深拷贝
		if (Gray.IsInitialized() && Gray.CountObj() > 0) { As.Gray = Gray.Clone(); };
		if (X.IsInitialized() && X.CountObj() > 0) { As.X = X.Clone(); };
		if (Y.IsInitialized() && Y.CountObj() > 0) { As.Y = Y.Clone(); };
		if (Z.IsInitialized() && Z.CountObj() > 0) { As.Z = Z.Clone(); };
		if (NX.IsInitialized() && NX.CountObj() > 0) { As.NX = NX.Clone(); };
		if (NY.IsInitialized() && NY.CountObj() > 0) { As.NY = NY.Clone(); };
		if (NZ.IsInitialized() && NZ.CountObj() > 0) { As.NZ = NZ.Clone(); };

		if (ObjectModel3D.Length() > 0)
		{
			CopyObjectModel3d(ObjectModel3D, "all", &As.ObjectModel3D);
		}

		As.ID = ID;

		return As;
	}


};





//预处理图像输入-3DS
class s_PreProcess3DSPara
{
public:
	double fRoiZMin;            //空间ROI区域范围
	double fRoiZMax;
	double fRoiXMin;
	double fRoiXMax;
	double fRoiYMin;
	double fRoiYMax;

	double fThSeg0Dis;              //初步分割  领域距离值  聚点数量选择 直径选择等
	int iThSeg0NumPtsMin;
	int iThSeg0NumPtsMax;
	double fThSeg0DiameterMin;
	double fThSeg0DiameterMax;


	bool bUseDisToPlane;           //进一步分割--使用到平面的距离
	double fSampleDtp = 10;
	double fThSegAngleDtp = 1.5;
	double fThSegDisDtp = 10;
	double fPtsSelToPlaneDisMin = 3;
	double fPtsSelToPlaneDisMax = 100;
	double fThSeg2DisDtp = 5;
	int iThSeg2NumPtsMinDtp = 5000;
	int iThSeg2NumPtsMaxDtp = 5000000;


	s_PreProcess3DSPara()
	{
		fRoiZMin = 0.0; //空间ROI区域范围
		fRoiZMax = 0.0;
		fRoiXMin = 0.0;
		fRoiXMax = 0.0;
		fRoiYMin = 0.0;
		fRoiYMax = 0.0;

		fThSeg0Dis = 0.0;              //初步分割  领域距离值  聚点数量选择 直径选择  Y方向聚类长度限制值等
		iThSeg0NumPtsMin = 0;
		iThSeg0NumPtsMax = 0;
		fThSeg0DiameterMin = 0.0;
		fThSeg0DiameterMax = 0.0;

		bUseDisToPlane = false;
		fSampleDtp = 10;
		fThSegAngleDtp = 1.5;
		fThSegDisDtp = 10;
		fPtsSelToPlaneDisMin = 3;
		fPtsSelToPlaneDisMax = 100;
		fThSeg2DisDtp = 5;
		iThSeg2NumPtsMinDtp = 5000;
		iThSeg2NumPtsMaxDtp = 5000000;
	}


	s_PreProcess3DSPara DeepCopy()
	{
		s_PreProcess3DSPara As;

		As.fRoiZMin = fRoiZMin;
		As.fRoiZMax = fRoiZMax;
		As.fRoiXMin = fRoiXMin;
		As.fRoiXMax = fRoiXMax;
		As.fRoiYMin = fRoiYMin;
		As.fRoiYMax = fRoiYMax;

		As.fThSeg0Dis = fThSeg0Dis;              //初步分割  领域距离值  聚点数量选择 直径选择  Y方向聚类长度限制值等
		As.iThSeg0NumPtsMin = iThSeg0NumPtsMin;
		As.iThSeg0NumPtsMax = iThSeg0NumPtsMax;
		As.fThSeg0DiameterMin = fThSeg0DiameterMin;
		As.fThSeg0DiameterMax = fThSeg0DiameterMax;

		As.bUseDisToPlane = bUseDisToPlane;
		As.fSampleDtp = fSampleDtp;
		As.fThSegAngleDtp = fThSegAngleDtp;
		As.fThSegDisDtp = fThSegDisDtp;
		As.fPtsSelToPlaneDisMin = fPtsSelToPlaneDisMin;
		As.fPtsSelToPlaneDisMax = fPtsSelToPlaneDisMax;
		As.fThSeg2DisDtp = fThSeg2DisDtp;
		As.iThSeg2NumPtsMinDtp = iThSeg2NumPtsMinDtp;
		As.iThSeg2NumPtsMaxDtp = iThSeg2NumPtsMaxDtp;


		return As;
	}

};


//预处理图像结果-3DS
class s_PreProcess3DSResultPara
{

public:
	bool bTJG;          //综合判断
	double time;
	s_Image3dS sImage3dPro;  //处理后的图像

	s_PreProcess3DSResultPara()
	{
		bTJG = false;
		time = 0.0;

	}

	s_PreProcess3DSResultPara DeepCopy()
	{
		s_PreProcess3DSResultPara As;

		As.bTJG = bTJG;
		As.time = time;
		As.sImage3dPro = sImage3dPro.DeepCopy();
		return As;
	}
};




//
//阴极板缺陷参数
class s_DefectPlateBPara
{
public:
	double fThNZAbsVal;
	double fThNXAbsVal;
	double fThNYAbsVal;
	double fThGrayVal;

	double fQgOffsetL;
	double fQgOffsetR;
	double fQgOffsetU;
	double fQgOffsetD;


	double fThBulgeLower;
	double fThBulgeHiger;

	double fQgHOrg;
	double fQgExCol;
	double fQgExRow;
	double fQgThOffset;

	double fConnectionDis;

	s_DefectPlateBPara()
	{

	}

	s_DefectPlateBPara DeepCopy()
	{
		s_DefectPlateBPara As;

		As.fThNZAbsVal = fThNZAbsVal;
		As.fThNXAbsVal = fThNXAbsVal;
		As.fThNYAbsVal = fThNYAbsVal;
		As.fThGrayVal = fThGrayVal;

		As.fQgOffsetL = fQgOffsetL;
		As.fQgOffsetR = fQgOffsetR;
		As.fQgOffsetU = fQgOffsetU;
		As.fQgOffsetD = fQgOffsetD;


		As.fThBulgeLower = fThBulgeLower;
		As.fThBulgeHiger = fThBulgeHiger;

		As.fQgHOrg = fQgHOrg;
		As.fQgExCol = fQgExCol;
		As.fQgExRow = fQgExRow;
		As.fQgThOffset = fQgThOffset;

		As.fConnectionDis = fConnectionDis;

		return As;
	}

};

//阴极板缺陷结果参数
class s_DefectPlateBRtsPara
{
public:
	bool bTJG;         //综合判断
	double time;

	HTuple PoseTb;

	HObject X1;
	HObject Y1;
	HObject Z1;
	HObject ImageSubZ1;
	HObject ImageZ1ZeroReal;

	HObject Z1PZero;
	HObject X1PZero;
	HObject Y1PZero;

	HObject RectPartLzC;
	HObject RectPartLzU;
	HObject RectPartLzL;
	HObject RectPartLzD;
	HObject RectPartLzR;

	HObject RectangleQgSort;

	HTuple OM3ImageAdv;      //3D结果  


	s_DefectPlateBRtsPara()
	{
		bTJG = false;
		time = 0.0;

		//数值结果
		PoseTb.Clear();

		//2D结果
		GenEmptyObj(&X1);
		GenEmptyObj(&Y1);
		GenEmptyObj(&Z1);
		GenEmptyObj(&ImageSubZ1);
		GenEmptyObj(&ImageZ1ZeroReal);
		GenEmptyObj(&Z1PZero);
		GenEmptyObj(&X1PZero);
		GenEmptyObj(&Y1PZero);
		GenEmptyObj(&RectPartLzC);
		GenEmptyObj(&RectPartLzU);
		GenEmptyObj(&RectPartLzL);
		GenEmptyObj(&RectPartLzD);
		GenEmptyObj(&RectPartLzR);


		GenEmptyObj(&RectangleQgSort);

		//3D结果  
		GenEmptyObjectModel3d(&OM3ImageAdv);


	}

	s_DefectPlateBRtsPara DeepCopy()
	{
		s_DefectPlateBRtsPara As;


		As.bTJG = bTJG;
		As.time = time;

		As.PoseTb = HTuple(PoseTb);

		//2D


		if (X1.IsInitialized() && X1.CountObj() > 0) { As.X1 = X1.Clone(); };
		if (Y1.IsInitialized() && Y1.CountObj() > 0) { As.Y1 = Y1.Clone(); };
		if (Z1.IsInitialized() && Z1.CountObj() > 0) { As.Z1 = Z1.Clone(); };


		if (ImageSubZ1.IsInitialized() && ImageSubZ1.CountObj() > 0) { As.ImageSubZ1 = ImageSubZ1.Clone(); };
		if (ImageZ1ZeroReal.IsInitialized() && ImageZ1ZeroReal.CountObj() > 0) { As.ImageZ1ZeroReal = ImageZ1ZeroReal.Clone(); };
		if (Z1PZero.IsInitialized() && Z1PZero.CountObj() > 0) { As.Z1PZero = Z1PZero.Clone(); };
		if (X1PZero.IsInitialized() && X1PZero.CountObj() > 0) { As.X1PZero = X1PZero.Clone(); };
		if (Y1PZero.IsInitialized() && Y1PZero.CountObj() > 0) { As.Y1PZero = Y1PZero.Clone(); };


		if (RectPartLzC.IsInitialized() && RectPartLzC.CountObj() > 0) { As.RectPartLzC = RectPartLzC.Clone(); };
		if (RectPartLzU.IsInitialized() && RectPartLzU.CountObj() > 0) { As.RectPartLzU = RectPartLzU.Clone(); };
		if (RectPartLzL.IsInitialized() && RectPartLzL.CountObj() > 0) { As.RectPartLzL = RectPartLzL.Clone(); };
		if (RectPartLzD.IsInitialized() && RectPartLzD.CountObj() > 0) { As.RectPartLzD = RectPartLzD.Clone(); };
		if (RectPartLzR.IsInitialized() && RectPartLzR.CountObj() > 0) { As.RectPartLzR = RectPartLzR.Clone(); };
		if (RectangleQgSort.IsInitialized() && RectangleQgSort.CountObj() > 0) { As.RectangleQgSort = RectangleQgSort.Clone(); };



		// 3D

		if (OM3ImageAdv.Length() > 0)
		{
			try { CopyObjectModel3d(OM3ImageAdv, "all", &As.OM3ImageAdv); }
			catch (...) { ; }

		}

		return As;
	}

	void Reset()
	{
		bTJG = false;
		time = 0.0;

		PoseTb.Clear();

		//2D
		X1.Clear();
		Y1.Clear();
		Z1.Clear();
		ImageSubZ1.Clear();
		ImageZ1ZeroReal.Clear();


		Z1PZero.Clear();
		X1PZero.Clear();
		Y1PZero.Clear();

		RectPartLzC.Clear();
		RectPartLzU.Clear();
		RectPartLzL.Clear();
		RectPartLzD.Clear();
		RectPartLzR.Clear();
		RectangleQgSort.Clear();


		GenEmptyObj(&X1);
		GenEmptyObj(&Y1);
		GenEmptyObj(&Z1);
		GenEmptyObj(&ImageSubZ1);
		GenEmptyObj(&ImageZ1ZeroReal);
		GenEmptyObj(&Z1PZero);
		GenEmptyObj(&X1PZero);
		GenEmptyObj(&Y1PZero);
		GenEmptyObj(&RectPartLzC);
		GenEmptyObj(&RectPartLzU);
		GenEmptyObj(&RectPartLzL);
		GenEmptyObj(&RectPartLzD);
		GenEmptyObj(&RectPartLzR);
		GenEmptyObj(&RectangleQgSort);

		//3D结果  
		GenEmptyObjectModel3d(&OM3ImageAdv);



		//3D
		if (OM3ImageAdv.Length() > 0)
		{
			ClearObjectModel3d(OM3ImageAdv);
			OM3ImageAdv.Clear();
		}


	}

};


//加工工艺参数
struct  s_JggyPara
{

	double fDjDiamiter;  //刀具直径
	double fJgLzUpOffset;  //粒子最高点上抬距离 作为最高点
	double fJgDpUpOffset; //铜板上平面上抬距离作为最低点
	int iModeJgPPZStepMode;//规划Z路径进给模式  0 :等距进给 1：线性进给
	double fJgPPZStepFix;
	double fJgPPZStepK;
	double fJgPPZStepB;
	int iModeJgPPYStepMode; //规划Y路径进给模式  0 :固定进给 2：根据刀盘大小进给
	double fJgPPYStepFix;
	double fJgPPYStepK;
	int iModeJgPPSort; //粒子加工排序 0：从上到下  1 ：从左到右
	double fQgSafeDis;  //气缸安全距离  注意此处考虑的是加工中心点到气缸的安全距离，未考虑刀盘直径影响
	double fJgTdZUp;     //抬刀高度 用于起始点 或者终点 加工完后的上抬高度


};

//路径点位结构体
struct s_PPts
{

	double fX;
	double fY;
	double fZ;
	int iDef; //点属性定义  1 起点  2 终点  3 中间点  4空跑点
	double fRow;  //图像行坐标
	double fCol;  //图像列坐标
	std::string strQgNotSafe; //避让气缸索引  eg "0,2,4" 代表第1,3,5个气缸需要松开

	s_PPts()
	{
		fX = 0;
		fY = 0;
		fZ = 0;
		iDef = 0;
		fRow = 0;
		fCol = 0;
		strQgNotSafe = "";
	}



	void Reset()
	{
		fX = 0;
		fY = 0;
		fZ = 0;
		iDef = 0;
		fRow = 0;
		fCol = 0;
		strQgNotSafe = "";
	}

};




//粒子路径规划结果参数结果参数
class s_LzppRtsPara
{
public:
	bool bTJG;         //综合判断
	double time;
	int iNumPts;
	std::vector<s_PPts> sListPPts;
	HObject RegionMxAllList;

	s_LzppRtsPara()
	{
		bTJG = false;
		time = 0.0;

		iNumPts = 0;
		sListPPts = {};
		GenEmptyObj(&RegionMxAllList);
	}


	s_LzppRtsPara DeepCopy()
	{
		s_LzppRtsPara As;


		As.bTJG = bTJG;
		As.time = time;

		As.iNumPts = iNumPts;
		As.sListPPts.clear();
		for (int i = 0; i < sListPPts.size(); i++)
		{
			As.sListPPts.push_back(sListPPts[i]);
		}


		if (RegionMxAllList.IsInitialized() && RegionMxAllList.CountObj() > 0) { As.RegionMxAllList = RegionMxAllList.Clone(); };

		return As;
	}

	void Reset()
	{
		bTJG = false;
		time = 0.0;

		iNumPts = 0;
		sListPPts.clear();
		GenEmptyObj(&RegionMxAllList);

	}
};



// 函数返回
struct s_Rtnf
{
public:
	int iCode = 0;                  // 返回代码
	std::string strInfo = "";                // 返回描述

};


