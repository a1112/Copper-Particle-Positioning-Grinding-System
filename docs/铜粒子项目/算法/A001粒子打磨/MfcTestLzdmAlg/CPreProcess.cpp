#include "pch.h"
#include "CPreProcess.h"


CPreProcess::CPreProcess()
{
}


CPreProcess::~CPreProcess()
{
}

s_Rtnf CPreProcess::OnPreProcess(s_Image3dS sImage3dS, s_PreProcess3DSPara spara1, s_PreProcess3DSResultPara& spara2)
{

	s_Rtnf sError;

	sError.iCode = -1;
	sError.strInfo = "";

	spara2.bTJG = false;
	spara2.time = 0.0;
	spara2.sImage3dPro.Clear();


	HTuple time_start = 0.0;
	HTuple time_end = 0.0;
	CountSeconds(&time_start);


	// Local iconic variables 
	HObject ho_X, ho_Y, ho_Z, ho_NX;
	HObject ho_NY, ho_NZ, /*ho_Texture ,*/ ho_GrayImage;
	HObject ho_Region, ho_X1, ho_Y1, ho_Z1;
	HObject ho_Region1, ho_Region2, ho_Region3;
	HObject ho_NX1, ho_NY1, ho_NZ1;
	HObject ho_Domain, ho_GrayImage1;

	HObject ho_Image1, ho_Image2;
	HObject ho_Image3, ho_ImageH, ho_ImageS;
	HObject ho_ImageV, ho_ImageR, ho_ImageG;
	HObject ho_ImageB, ho_Multichannel;

	// Local control variables 

	HTuple hv_ImageWidth;
	HTuple hv_ImageHeight, hv_WindowWidth;
	HTuple hv_WindowHeight;
	HTuple hv_GenParamName, hv_GenParamValue;

	HTuple hv_ObjectModel3D;
	HTuple hv_Rows, hv_Columns;
	HTuple hv_NXV, hv_NYV, hv_NZV;
	HTuple hv_Intensity, hv_Pose;
	HTuple hv_ObjectModel3DConnected, hv_ObjectModel3DSelected;
	HTuple hv_ObjectModel3DSelected2, hv_UnionObjectModel3D;

	HTuple hv_SampledObjectModel3DS1;
	HTuple hv_ObjectModel3DConnectedS1, hv_GPVS1;
	HTuple hv_MaxS1, hv_ObjectModel3DSelectedS1a;
	HTuple hv_ObjectModel3DConnectedS1a, hv_GPVS1a;
	HTuple hv_MaxS1a, hv_ObjectModel3DSelectedS1b;
	HTuple hv_UnionObjectModel3DS1, hv_OM3DPlane;
	HTuple hv_ParFitting, hv_ValFitting;
	HTuple hv_ObjectModel3DOutID, hv_GenParamPosePlane;
	HTuple hv_PlaneDatum, hv_GenParamValueDistancePlane;
	HTuple hv_ObjectModel3DThresholdedS1c, hv_PoseOutA;
	HTuple hv_UnionObjectModel3DS12, hv_ObjectModel3DConnectedS1d;
	HTuple hv_ObjectModel3DSelectedS1d;


	HTuple hv_RV, hv_GV, hv_BV;
	HTuple hv_GvBoundingBox1S0;
	HTuple hv_lObjectModel3DS0, hv_ObjectModel3DSelectedS0;

	HTuple hv_NumPts;

	// Initialize local and output iconic variables 
	GenEmptyObj(&ho_X);
	GenEmptyObj(&ho_Y);
	GenEmptyObj(&ho_Z);
	GenEmptyObj(&ho_NX);
	GenEmptyObj(&ho_NY);
	GenEmptyObj(&ho_NZ);
	//HOperatorSet.GenEmptyObj(&ho_Texture);
	GenEmptyObj(&ho_GrayImage);
	GenEmptyObj(&ho_Region);
	GenEmptyObj(&ho_Region1);
	GenEmptyObj(&ho_Region2);
	GenEmptyObj(&ho_Region3);
	GenEmptyObj(&ho_X1);
	GenEmptyObj(&ho_Y1);
	GenEmptyObj(&ho_Z1);
	GenEmptyObj(&ho_NX1);
	GenEmptyObj(&ho_NY1);
	GenEmptyObj(&ho_NZ1);
	GenEmptyObj(&ho_Domain);
	GenEmptyObj(&ho_GrayImage1);

	GenEmptyObj(&ho_Image1);
	GenEmptyObj(&ho_Image2);
	GenEmptyObj(&ho_Image3);
	GenEmptyObj(&ho_ImageH);
	GenEmptyObj(&ho_ImageS);
	GenEmptyObj(&ho_ImageV);
	GenEmptyObj(&ho_ImageR);
	GenEmptyObj(&ho_ImageG);
	GenEmptyObj(&ho_ImageB);
	GenEmptyObj(&ho_Multichannel);

	try
	{

		s_Image3dS Image = sImage3dS;


		//判断输入
		if (!Image.Z.IsInitialized() || Image.Z.CountObj() == 0)
		{
			CountSeconds(&time_end);
			spara2.time = time_end - time_start;

			sError.iCode = 1;
			sError.strInfo = "图像为空!";
			return sError;
		}


		//处理算法




		//ROI区域图像 并给点云附加属性

		Threshold(Image.Z, &ho_Region1, spara1.fRoiZMin, spara1.fRoiZMax);
		Threshold(Image.X, &ho_Region2, spara1.fRoiXMin, spara1.fRoiXMax);
		Threshold(Image.Y, &ho_Region3, spara1.fRoiYMin, spara1.fRoiYMax);
		Intersection(ho_Region1, ho_Region2, &ho_Region);
		Intersection(ho_Region3, ho_Region, &ho_Region);


		ReduceDomain(Image.X, ho_Region, &ho_X);
		ReduceDomain(Image.Y, ho_Region, &ho_Y);
		ReduceDomain(Image.Z, ho_Region, &ho_Z);
		ReduceDomain(Image.NX, ho_Region, &ho_NX);
		ReduceDomain(Image.NY, ho_Region, &ho_NY);
		ReduceDomain(Image.NZ, ho_Region, &ho_NZ);
		ReduceDomain(Image.Gray, ho_Region, &ho_GrayImage);

		////灰度自动调整
		//{
		//    HTuple hv_Min = new HTuple(), hv_Max = new HTuple(), hv_Range = new HTuple(), hv_Mean = new HTuple(), hv_Deviation = new HTuple();

		//    HObject ho_ROI_0, ho_ImageTextureReduced, ho_ImageScaled;
		//   GenEmptyObj(&ho_ROI_0);
		//   GenEmptyObj(&ho_ImageTextureReduced);
		//   GenEmptyObj(&ho_ImageScaled);


		//    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
		//   MinMaxGray(ho_GrayImage, ho_GrayImage, 0, &hv_Min, &hv_Max,
		//        &hv_Range);
		//    ho_ROI_0.Dispose();
		//   GenRectangle1(&ho_ROI_0, 565.043, 729.802, 1220.68, 1362.76);
		//    ho_ImageTextureReduced.Dispose();
		//   ReduceDomain(ho_GrayImage, ho_ROI_0, &ho_ImageTextureReduced
		//    );
		//    hv_Mean.Dispose(); hv_Deviation.Dispose();
		//   Intensity(ho_ROI_0, ho_ImageTextureReduced, &hv_Mean, &hv_Deviation);
		//    using (HDevDisposeHelper dh = new HDevDisposeHelper())
		//    {
		//        ho_ImageScaled.Dispose();
		//        new HVisionAdv().scale_image_range(ho_GrayImage, &ho_ImageScaled, (new HTuple(0)).TupleConcat(
		//            0), ((hv_Mean * 1.2)).TupleConcat(255));
		//    }
		//    ho_GrayImage.Dispose();
		//   CopyImage(ho_ImageScaled, &ho_GrayImage);

		//}


		XyzToObjectModel3d(ho_X, ho_Y, ho_Z, &hv_ObjectModel3D);
		GetObjectModel3dParams(hv_ObjectModel3D, "num_points", &hv_NumPts);
		GetRegionPoints(ho_Region, &hv_Rows, &hv_Columns);




		//法线属性
		try
		{

			GetGrayval(ho_NX, hv_Rows, hv_Columns, &hv_NXV);
			GetGrayval(ho_NY, hv_Rows, hv_Columns, &hv_NYV);
			GetGrayval(ho_NZ, hv_Rows, hv_Columns, &hv_NZV);


			SetObjectModel3dAttribMod(hv_ObjectModel3D, ((HTuple("point_normal_x").Append("point_normal_y")).Append("point_normal_z")),
				HTuple(), (hv_NXV.TupleConcat(hv_NYV)).TupleConcat(hv_NZV));

		}
		catch (...)
		{


		}


		//灰度属性
		try
		{

			GetGrayval(ho_GrayImage, hv_Rows, hv_Columns, &hv_Intensity);
			SetObjectModel3dAttribMod(hv_ObjectModel3D, "&intensity", "points", hv_Intensity);
		}
		catch (...)
		{


		}



		try
		{
			//法线渲染成RGB


			ScaleImageMax(ho_NX, &ho_Image1);
			ScaleImageMax(ho_NY, &ho_Image2);
			ScaleImageMax(ho_NZ, &ho_Image3);
			TransFromRgb(ho_Image1, ho_Image2, ho_Image3, &ho_ImageH, &ho_ImageS, &ho_ImageV, "hsv");
			TransToRgb(ho_ImageH, ho_ImageS, ho_ImageV, &ho_ImageR, &ho_ImageG, &ho_ImageB, "hsv");
			Compose3(ho_ImageR, ho_ImageG, ho_ImageB, &ho_Multichannel);

			GetGrayval(ho_ImageR, hv_Rows, hv_Columns, &hv_RV);
			GetGrayval(ho_ImageG, hv_Rows, hv_Columns, &hv_GV);
			GetGrayval(ho_ImageB, hv_Rows, hv_Columns, &hv_BV);
			SetObjectModel3dAttribMod(hv_ObjectModel3D, "&red", "points", hv_RV);
			SetObjectModel3dAttribMod(hv_ObjectModel3D, "&green", "points", hv_GV);
			SetObjectModel3dAttribMod(hv_ObjectModel3D, "&blue", "points", hv_BV);
		}
		catch (...)
		{


		}





		//聚类分割  根据点数 直径
		if (true)
		{

			ConnectionObjectModel3d(hv_ObjectModel3D, "distance_3d", spara1.fThSeg0Dis,
				&hv_ObjectModel3DConnected);

			SelectObjectModel3d(hv_ObjectModel3DConnected, "num_points",
				"and", spara1.iThSeg0NumPtsMin, spara1.iThSeg0NumPtsMax, &hv_ObjectModel3DSelected);

			SelectObjectModel3d(hv_ObjectModel3DSelected, "diameter_bounding_box",
				"and", spara1.fThSeg0DiameterMin, spara1.fThSeg0DiameterMax, &hv_ObjectModel3DSelected2);

			UnionObjectModel3d(hv_ObjectModel3DSelected2, "points_surface", &hv_UnionObjectModel3D);
		}




		GetObjectModel3dParams(hv_UnionObjectModel3D, "num_points", &hv_NumPts);

		//根据处理后点云区域 获得XYZ NXYZ Gray 

		ObjectModel3dToXyz(&ho_X1, &ho_Y1, &ho_Z1, hv_UnionObjectModel3D, "from_xyz_map", HTuple(), HTuple());

		GetDomain(ho_Z1, &ho_Domain);

		//HOperatorSet.ReduceDomain(ho_X, ho_Domain, &ho_X1);
		//HOperatorSet.ReduceDomain(ho_Y, ho_Domain, &ho_Y1);
		//HOperatorSet.ReduceDomain(ho_Z, ho_Domain, &ho_Z1);
		ReduceDomain(ho_NX, ho_Domain, &ho_NX1);
		ReduceDomain(ho_NY, ho_Domain, &ho_NY1);
		ReduceDomain(ho_NZ, ho_Domain, &ho_NZ1);

		ReduceDomain(ho_GrayImage, ho_Domain, &ho_GrayImage1);


		//结果数据

		spara2.sImage3dPro.ID = Image.ID;

		if (hv_UnionObjectModel3D.Length() > 0)
		{
			CopyObjectModel3d(hv_UnionObjectModel3D, "all", &spara2.sImage3dPro.ObjectModel3D);
		}

		spara2.sImage3dPro.Gray = ho_GrayImage1.Clone();
		spara2.sImage3dPro.X = ho_X1.Clone();
		spara2.sImage3dPro.Y = ho_Y1.Clone();
		spara2.sImage3dPro.Z = ho_Z1.Clone();
		spara2.sImage3dPro.NX = ho_NX1.Clone();
		spara2.sImage3dPro.NY = ho_NY1.Clone();
		spara2.sImage3dPro.NZ = ho_NZ1.Clone();


		//释放所有临时变量


		spara2.bTJG = true;

		CountSeconds(&time_end);
		spara2.time = time_end - time_start;


		sError.iCode = 0;
		sError.strInfo = "";
		return sError;
	}
	catch (HalconCpp::HException& ex)
	{


		//string str = ex.ToString();
		//CLogTxt.WriteTxt(str);

		CountSeconds(&time_end);
		spara2.time = time_end - time_start;

		sError.iCode = -1;
		sError.strInfo = "预处理失败!";
		return sError;

	}
}




