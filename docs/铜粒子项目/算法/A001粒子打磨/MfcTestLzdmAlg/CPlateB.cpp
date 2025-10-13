#include "pch.h"
#include "CPlateB.h"



CPlateB::CPlateB()
{
}


CPlateB::~CPlateB()
{
}





s_Rtnf CPlateB::OnDetect(s_Image3dS Image3d, s_DefectPlateBPara spara1, s_DefectPlateBRtsPara& spara2)
{

	HTuple time_start = 0.0;
	HTuple time_end = 0.0;
	CountSeconds(&time_start);

	s_Rtnf sError;
	sError.iCode = -1;
	sError.strInfo = "";


	//复位结果数据
	spara2.Reset();



	// Local iconic variables 

	HObject ho_Region, ho_PointCloud;
	HObject ho_Normals, ho_X, ho_Y, ho_Gray;
	HObject ho_Z, ho_NX, ho_NY, ho_NZ, ho_MultiChannelImage;
	HObject ho_Region1, ho_Region2, ho_RegionNZ;
	HObject ho_Region3, ho_Region4, ho_RegionNXY;
	HObject ho_RegionRegionNXYZ, ho_RegionIntersection;
	HObject ho_ImageReduced, ho_Xs, ho_Ys, ho_Zs;
	HObject ho_Domain, ho_RegionFillUp, ho_RegionClosing;
	HObject ho_RegionOpening, ho_RegionErosion, ho_RegionTb;
	HObject ho_X1, ho_Y1, ho_Z1, ho_ROI;
	HObject ho_ImageSurface, ho_ImageSub, ho_ConnectedRegions;
	HObject ho_SelectedRegions, ho_RectangleQg, ho_RectangleL;
	HObject ho_RectangleR, ho_RectangleU, ho_RectangleD;
	HObject ho_RegionDifference, ho_RectangleQgL;
	HObject ho_RectangleQgR, ho_RectangleQgU, ho_RectangleQgD;
	HObject ho_RectangleLAdv, ho_RectangleRAdv, ho_RectangleUAdv;
	HObject ho_RectangleDAdv, ho_RectangleCAdv, ho_RectanglePartList;
	HObject ho_RectangleQgSort, ho_SortedRegions;
	HObject ho_ImageSubZ1, ho_X1PZeroC, ho_Y1PZeroC;
	HObject ho_Z1PZeroC, ho_RegionRoiCBulge, ho_ImageSubC;
	HObject ho_Z1PZero, ho_X1PZero, ho_Y1PZero;
	HObject ho_RegionRoiCBulgeUnion, ho_RectangleQgEx;
	HObject ho_RectangleLAdvRemoveQg, ho_X1PZeroL;
	HObject ho_Y1PZeroL, ho_Z1PZeroL, ho_Z1PZeroLRemoveQg;
	HObject ho_RegionQgExL, ho_RegionRoiLBulgeRemoveQg;
	HObject ho_ImageSubLRemoveQg, ho_RegionUnion;
	HObject ho_RegionRoiLBulgeQg, ho_ImageSubLQg;
	HObject ho_RectangleRAdvRemoveQg, ho_X1PZeroR;
	HObject ho_Y1PZeroR, ho_Z1PZeroR, ho_Z1PZeroRRemoveQg;
	HObject ho_RegionQgExR, ho_RegionRoiRBulgeRemoveQg;
	HObject ho_ImageSubRRemoveQg, ho_RegionRoiRBulgeQg;
	HObject ho_ImageSubRQg, ho_RectangleUAdvRemoveQg;
	HObject ho_X1PZeroU, ho_Y1PZeroU, ho_Z1PZeroU;
	HObject ho_Z1PZeroURemoveQg, ho_RegionQgExU, ho_RegionRoiUBulgeRemoveQg;
	HObject ho_ImageSubURemoveQg, ho_RegionRoiUBulgeQg;
	HObject ho_ImageSubUQg, ho_RectangleDAdvRemoveQg;
	HObject ho_X1PZeroD, ho_Y1PZeroD, ho_Z1PZeroD;
	HObject ho_Z1PZeroDRemoveQg, ho_RegionQgExD, ho_RegionRoiDBulgeRemoveQg;
	HObject ho_ImageSubDRemoveQg, ho_RegionRoiDBulgeQg;
	HObject ho_ImageSubDQg, ho_RegionRoiLBulge, ho_RegionRoiRBulge;
	HObject ho_RegionRoiUBulge, ho_RegionRoiDBulge;
	HObject ho_RegionPartLzC, ho_RectPartLzC, ho_RegionPartLzL;
	HObject ho_RectPartLzL, ho_RegionPartLzR, ho_RectPartLzR;
	HObject ho_RegionPartUzL, ho_RectPartLzU, ho_RegionPartLzD;
	HObject ho_RectPartLzD;
	HObject hImageRed, hImageGreen, hImageBlue;


	HObject ho_ImageZ1ZeroReal, ho_ZZeroRealC, ho_ZZeroRealL, ho_ZZeroRealR, ho_ZZeroRealU, ho_ZZeroRealD;
	HObject ho_ZZeroRealLQg, ho_ZZeroRealRQg, ho_ZZeroRealUQg, ho_ZZeroRealDQg;
	HObject ho_RegionMoved;

	HObject ho_ROI_0, ho_ROI_1, ho_ROI_2, ho_ROI_3;
	HObject ho_ROI_4, ho_ROI_5, ho_ROI_6, ho_ROI_7;
	HObject ho_ROI_8, ho_ROI_9, ho_ROI_10, ho_ROI_11;
	HObject ho_ROI_12, ho_ROI_13, ho_ROI_14, ho_ROI_15;
	HObject ho_RegionQgIn;


	HObject ho_RegionQgReal, ho_ObjectSelected1, ho_ObjectSelected2, ho_EmptyRegion;

	// Local control variables 

	HTuple hv_Rows, hv_Columns;
	HTuple hv_Max, hv_ObjectModel3DConnected;
	HTuple hv_ObjectModel3DSelected, hv_UnionObjectModel3D;
	HTuple hv_Om3DScene, hv_fThNZAbsVal;
	HTuple hv_fThNXAbsVal, hv_fThNYAbsVal;
	HTuple hv_fThGrayVal, hv_ObjectModel3D1;
	HTuple hv_GenParamValue, hv_ObjectModel3DAdv;
	HTuple hv_Alpha, hv_Beta;
	HTuple hv_Gamma, hv_Area;
	HTuple hv_Row, hv_Column;
	HTuple hv_Width, hv_Height;
	HTuple hv_Row1, hv_Column1;
	HTuple hv_Row2, hv_Column2;
	HTuple hv_Diameter, hv_Rectangularity;
	HTuple hv_fQgOffsetL, hv_fQgOffsetR;
	HTuple hv_fQgOffsetU, hv_fQgOffsetD;
	HTuple hv_ColumnL, hv_ColumnR;
	HTuple hv_RowU, hv_RowD;
	HTuple hv_Om3DC, hv_SampledObjectModel3D;
	HTuple hv_OM3DPlane, hv_ParFitting;
	HTuple hv_ValFitting, hv_ObjectModel3DOutID;
	HTuple hv_GenParamPosePlane, hv_PlaneDatum;
	HTuple hv_PoseTbC, hv_PoseInvert;
	HTuple hv_HomMat3D, hv_OM3dPZeroC;
	HTuple hv_fThBulgeLower, hv_fThBulgeHiger;
	HTuple hv_Grayval, hv_fQgHOrg;
	HTuple hv_fQgExCol, hv_fQgExRow;
	HTuple hv_fQgThOffset, hv_Om3DL;
	HTuple hv_Om3DLRemoveQg;
	HTuple hv_OM3dPZeroL, hv_Om3DR;
	HTuple hv_Om3DRRemoveQg;
	HTuple hv_OM3dPZeroR, hv_Om3DU;
	HTuple hv_Om3DURemoveQg;
	HTuple hv_OM3dPZeroU, hv_Om3DD;
	HTuple hv_Om3DDRemoveQg;
	HTuple hv_OM3dPZeroD, hv_fConnectionDis;

	HTuple hv_OM3dPZero;


	HTuple hChannels;

	HTuple hv_bFind;
	HTuple hv_Number1;
	HTuple hv_Number2;
	HTuple hv_i;
	HTuple hv_j;

	// Initialize local and output iconic variables 
	GenEmptyObj(&ho_Region);
	GenEmptyObj(&ho_PointCloud);
	GenEmptyObj(&ho_Normals);
	GenEmptyObj(&ho_X);
	GenEmptyObj(&ho_Y);
	GenEmptyObj(&ho_Z);
	GenEmptyObj(&ho_Gray);
	GenEmptyObj(&ho_NX);
	GenEmptyObj(&ho_NY);
	GenEmptyObj(&ho_NZ);
	GenEmptyObj(&ho_MultiChannelImage);
	GenEmptyObj(&ho_Region1);
	GenEmptyObj(&ho_Region2);
	GenEmptyObj(&ho_RegionNZ);
	GenEmptyObj(&ho_Region3);
	GenEmptyObj(&ho_Region4);
	GenEmptyObj(&ho_RegionNXY);
	GenEmptyObj(&ho_RegionRegionNXYZ);
	GenEmptyObj(&ho_RegionIntersection);
	GenEmptyObj(&ho_ImageReduced);
	GenEmptyObj(&ho_Xs);
	GenEmptyObj(&ho_Ys);
	GenEmptyObj(&ho_Zs);
	GenEmptyObj(&ho_Domain);
	GenEmptyObj(&ho_RegionFillUp);
	GenEmptyObj(&ho_RegionClosing);
	GenEmptyObj(&ho_RegionOpening);
	GenEmptyObj(&ho_RegionErosion);
	GenEmptyObj(&ho_RegionTb);
	GenEmptyObj(&ho_X1);
	GenEmptyObj(&ho_Y1);
	GenEmptyObj(&ho_Z1);

	GenEmptyObj(&ho_ROI);
	GenEmptyObj(&ho_ImageSurface);
	GenEmptyObj(&ho_ImageSub);
	GenEmptyObj(&ho_ConnectedRegions);
	GenEmptyObj(&ho_SelectedRegions);
	GenEmptyObj(&ho_RectangleQg);
	GenEmptyObj(&ho_RectangleL);
	GenEmptyObj(&ho_RectangleR);
	GenEmptyObj(&ho_RectangleU);
	GenEmptyObj(&ho_RectangleD);
	GenEmptyObj(&ho_RegionDifference);
	GenEmptyObj(&ho_RectangleQgL);
	GenEmptyObj(&ho_RectangleQgR);
	GenEmptyObj(&ho_RectangleQgU);
	GenEmptyObj(&ho_RectangleQgD);
	GenEmptyObj(&ho_RectangleLAdv);
	GenEmptyObj(&ho_RectangleRAdv);
	GenEmptyObj(&ho_RectangleUAdv);
	GenEmptyObj(&ho_RectangleDAdv);
	GenEmptyObj(&ho_RectangleCAdv);
	GenEmptyObj(&ho_RectanglePartList);
	GenEmptyObj(&ho_RectangleQgSort);
	GenEmptyObj(&ho_SortedRegions);
	GenEmptyObj(&ho_ImageSubZ1);
	GenEmptyObj(&ho_X1PZeroC);
	GenEmptyObj(&ho_Y1PZeroC);
	GenEmptyObj(&ho_Z1PZeroC);
	GenEmptyObj(&ho_X1PZero);
	GenEmptyObj(&ho_Y1PZero);
	GenEmptyObj(&ho_Z1PZero);
	GenEmptyObj(&ho_RegionRoiCBulge);
	GenEmptyObj(&ho_ImageSubC);
	GenEmptyObj(&ho_RegionRoiCBulgeUnion);
	GenEmptyObj(&ho_RectangleQgEx);
	GenEmptyObj(&ho_RectangleLAdvRemoveQg);
	GenEmptyObj(&ho_X1PZeroL);
	GenEmptyObj(&ho_Y1PZeroL);
	GenEmptyObj(&ho_Z1PZeroL);
	GenEmptyObj(&ho_Z1PZeroLRemoveQg);
	GenEmptyObj(&ho_RegionQgExL);
	GenEmptyObj(&ho_RegionRoiLBulgeRemoveQg);
	GenEmptyObj(&ho_ImageSubLRemoveQg);
	GenEmptyObj(&ho_RegionUnion);
	GenEmptyObj(&ho_RegionRoiLBulgeQg);
	GenEmptyObj(&ho_ImageSubLQg);
	GenEmptyObj(&ho_RectangleRAdvRemoveQg);
	GenEmptyObj(&ho_X1PZeroR);
	GenEmptyObj(&ho_Y1PZeroR);
	GenEmptyObj(&ho_Z1PZeroR);
	GenEmptyObj(&ho_Z1PZeroRRemoveQg);
	GenEmptyObj(&ho_RegionQgExR);
	GenEmptyObj(&ho_RegionRoiRBulgeRemoveQg);
	GenEmptyObj(&ho_ImageSubRRemoveQg);
	GenEmptyObj(&ho_RegionRoiRBulgeQg);
	GenEmptyObj(&ho_ImageSubRQg);
	GenEmptyObj(&ho_RectangleUAdvRemoveQg);
	GenEmptyObj(&ho_X1PZeroU);
	GenEmptyObj(&ho_Y1PZeroU);
	GenEmptyObj(&ho_Z1PZeroU);
	GenEmptyObj(&ho_Z1PZeroURemoveQg);
	GenEmptyObj(&ho_RegionQgExU);
	GenEmptyObj(&ho_RegionRoiUBulgeRemoveQg);
	GenEmptyObj(&ho_ImageSubURemoveQg);
	GenEmptyObj(&ho_RegionRoiUBulgeQg);
	GenEmptyObj(&ho_ImageSubUQg);
	GenEmptyObj(&ho_RectangleDAdvRemoveQg);
	GenEmptyObj(&ho_X1PZeroD);
	GenEmptyObj(&ho_Y1PZeroD);
	GenEmptyObj(&ho_Z1PZeroD);
	GenEmptyObj(&ho_Z1PZeroDRemoveQg);
	GenEmptyObj(&ho_RegionQgExD);
	GenEmptyObj(&ho_RegionRoiDBulgeRemoveQg);
	GenEmptyObj(&ho_ImageSubDRemoveQg);
	GenEmptyObj(&ho_RegionRoiDBulgeQg);
	GenEmptyObj(&ho_ImageSubDQg);
	GenEmptyObj(&ho_RegionRoiLBulge);
	GenEmptyObj(&ho_RegionRoiRBulge);
	GenEmptyObj(&ho_RegionRoiUBulge);
	GenEmptyObj(&ho_RegionRoiDBulge);
	GenEmptyObj(&ho_RegionPartLzC);
	GenEmptyObj(&ho_RectPartLzC);
	GenEmptyObj(&ho_RegionPartLzL);
	GenEmptyObj(&ho_RectPartLzL);
	GenEmptyObj(&ho_RegionPartLzR);
	GenEmptyObj(&ho_RectPartLzR);
	GenEmptyObj(&ho_RegionPartUzL);
	GenEmptyObj(&ho_RectPartLzU);
	GenEmptyObj(&ho_RegionPartLzD);
	GenEmptyObj(&ho_RectPartLzD); ;


	GenEmptyObj(&hImageRed);
	GenEmptyObj(&hImageGreen);
	GenEmptyObj(&hImageBlue); ;


	GenEmptyObj(&ho_ImageZ1ZeroReal);
	GenEmptyObj(&ho_ZZeroRealC);
	GenEmptyObj(&ho_ZZeroRealL);
	GenEmptyObj(&ho_ZZeroRealR);
	GenEmptyObj(&ho_ZZeroRealU);
	GenEmptyObj(&ho_ZZeroRealD);
	GenEmptyObj(&ho_ZZeroRealLQg);
	GenEmptyObj(&ho_ZZeroRealRQg);
	GenEmptyObj(&ho_ZZeroRealUQg);
	GenEmptyObj(&ho_ZZeroRealDQg);
	GenEmptyObj(&ho_RegionMoved);

	GenEmptyObj(&ho_ROI_0);
	GenEmptyObj(&ho_ROI_1);
	GenEmptyObj(&ho_ROI_2);
	GenEmptyObj(&ho_ROI_3);
	GenEmptyObj(&ho_ROI_4);
	GenEmptyObj(&ho_ROI_5);
	GenEmptyObj(&ho_ROI_6);
	GenEmptyObj(&ho_ROI_7);
	GenEmptyObj(&ho_ROI_8);
	GenEmptyObj(&ho_ROI_9);
	GenEmptyObj(&ho_ROI_10);
	GenEmptyObj(&ho_ROI_11);
	GenEmptyObj(&ho_ROI_12);
	GenEmptyObj(&ho_ROI_13);
	GenEmptyObj(&ho_ROI_14);
	GenEmptyObj(&ho_ROI_15);
	GenEmptyObj(&ho_RegionQgIn);


	GenEmptyObj(&ho_RegionQgReal);
	GenEmptyObj(&ho_ObjectSelected1);
	GenEmptyObj(&ho_ObjectSelected2);
	GenEmptyObj(&ho_EmptyRegion);




	while (true)
	{
		try
		{


			ho_X = Image3d.X.Clone();
			ho_Y = Image3d.Y.Clone();
			ho_Z = Image3d.Z.Clone();
			ho_Gray = Image3d.Gray.Clone();

			ho_NX = Image3d.NX.Clone();
			ho_NY = Image3d.NY.Clone();
			ho_NZ = Image3d.NZ.Clone();


			//new HVisionAdv().WriteImage3DX(Image3d,@"D:\\lins","1");

			//判断输入
			if (!ho_Z.IsInitialized() || ho_Z.CountObj() == 0 || !ho_X.IsInitialized() || ho_X.CountObj() == 0 || !ho_Y.IsInitialized() || ho_Y.CountObj() == 0)
			{
				CountSeconds(&time_end);
				spara2.time = time_end - time_start;

				sError.iCode = 1;
				sError.strInfo = "图像为空!";
				break;
			}


			if (!ho_NZ.IsInitialized() || ho_NZ.CountObj() == 0 || !ho_NX.IsInitialized() || ho_NX.CountObj() == 0 || !ho_NY.IsInitialized() || ho_NY.CountObj() == 0)
			{
				CountSeconds(&time_end);
				spara2.time = time_end - time_start;

				sError.iCode = 1;
				sError.strInfo = "图像为空!";
				break;
			}


			if (!ho_Gray.IsInitialized() || ho_Gray.CountObj() == 0)
			{
				CountSeconds(&time_end);
				spara2.time = time_end - time_start;

				sError.iCode = 1;
				sError.strInfo = "图像为空!";
				break;
			}


			//3通道图像转成单通道
			CountChannels(ho_Gray, &hChannels);
			if (hChannels[0].I() == 3)
			{
				Decompose3(ho_Gray, &hImageRed, &hImageGreen, &hImageBlue);
				ho_Gray = hImageRed.Clone();
			}


			GenRectangle1(&ho_ROI_0, 428, 753, 591, 831);
			GenRectangle1(&ho_ROI_1, 433, 916, 618, 1001);
			GenRectangle1(&ho_ROI_2, 433, 1084, 628, 1171);
			GenRectangle1(&ho_ROI_3, 421, 1264, 611, 1331);

			GenRectangle1(&ho_ROI_4, 671.403, 1277.93, 746.476, 1460.56);
			GenRectangle1(&ho_ROI_5, 804.032, 1290.44, 879.105, 1473.07);
			GenRectangle1(&ho_ROI_6, 969.192, 1277.93, 1044.26, 1460.56);
			GenRectangle1(&ho_ROI_7, 1101.82, 1285.43, 1176.89, 1468.07);


			GenRectangle1(&ho_ROI_8, 1189.41, 1204.13, 1299.51, 1249.16);
			GenRectangle1(&ho_ROI_9, 1174.39, 1096.55, 1284.5, 1141.58);
			GenRectangle1(&ho_ROI_10, 1169.96, 941.503, 1280.07, 999.045);
			GenRectangle1(&ho_ROI_11, 1168.19, 801.624, 1278.3, 859.166);

			GenRectangle1(&ho_ROI_12, 1095.66, 630.369, 1145.2, 786.024);
			GenRectangle1(&ho_ROI_13, 976.981, 637.452, 1037.13, 793.106);
			GenRectangle1(&ho_ROI_14, 813.996, 645.419, 874.147, 801.074);
			GenRectangle1(&ho_ROI_15, 631.69, 627.725, 691.841, 783.38);


			GenEmptyObj(&ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_0, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_1, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_2, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_3, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_4, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_5, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_6, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_7, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_8, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_9, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_10, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_11, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_12, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_13, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_14, &ho_RegionQgIn);
			ConcatObj(ho_RegionQgIn, ho_ROI_15, &ho_RegionQgIn);


			//step1 各种ROI区域/点云

			//铜板整体区域
			XyzToObjectModel3d(ho_X, ho_Y, ho_Z, &hv_Om3DScene);

			//提取铜板整体参数
			hv_fThNZAbsVal = /*0.8*/spara1.fThNZAbsVal;
			hv_fThNXAbsVal = /*0.2*/spara1.fThNXAbsVal;
			hv_fThNYAbsVal = /*0.2*/spara1.fThNYAbsVal;
			hv_fThGrayVal = /*50*/spara1.fThGrayVal;


			Threshold(ho_NZ, &ho_Region1, -1, -hv_fThNZAbsVal);
			Threshold(ho_NZ, &ho_Region2, hv_fThNZAbsVal, 1);
			Union2(ho_Region1, ho_Region2, &ho_RegionNZ);


			Threshold(ho_NX, &ho_Region3, -hv_fThNXAbsVal, hv_fThNXAbsVal);
			Threshold(ho_NY, &ho_Region4, -hv_fThNYAbsVal, hv_fThNYAbsVal);
			Intersection(ho_Region4, ho_Region3, &ho_RegionNXY);
			Intersection(ho_RegionNZ, ho_RegionNXY, &ho_RegionRegionNXYZ);
			Intersection(ho_RegionRegionNXYZ, ho_Z, &ho_RegionIntersection);


			Threshold(ho_Gray, &ho_Region, hv_fThGrayVal, 255);
			Intersection(ho_Region, ho_RegionIntersection, &ho_RegionIntersection);
			ReduceDomain(ho_Z, ho_RegionIntersection, &ho_ImageReduced);


			XyzToObjectModel3d(ho_X, ho_Y, ho_ImageReduced, &hv_ObjectModel3D1);


			//HOperatorSet.WriteImage(ho_X, "tiff", 0, @"D:\\lins\\" + @"ho_X");
			//HOperatorSet.WriteImage(ho_Y, "tiff", 0, @"D:\\lins\\" + @"ho_Y");
			//HOperatorSet.WriteImage(ho_ImageReduced, "tiff", 0, @"D:\\lins\\" + @"ho_ImageReduced");
			//  new HVisionAdv().WriteRegionX(ho_RegionIntersection, @"D:\\lins\\", @"ho_RegionIntersection", true);


			ConnectionObjectModel3d(hv_ObjectModel3D1, "distance_3d", 5, &hv_ObjectModel3DConnected);
			GetObjectModel3dParams(hv_ObjectModel3DConnected, "num_points", &hv_GenParamValue);
			TupleMax(hv_GenParamValue, &hv_Max);
			SelectObjectModel3d(hv_ObjectModel3DConnected, "num_points", "and", hv_Max, hv_Max, &hv_ObjectModel3DSelected);

			ObjectModel3dToXyz(&ho_Xs, &ho_Ys, &ho_Zs, hv_ObjectModel3DSelected, "from_xyz_map", HTuple(), HTuple());

			GetDomain(ho_Xs, &ho_Domain);

			FillUp(ho_Domain, &ho_RegionFillUp);

			ClosingRectangle1(ho_RegionFillUp, &ho_RegionClosing, 101, 101);

			OpeningRectangle1(ho_RegionClosing, &ho_RegionOpening, 151, 151);

			ErosionRectangle1(ho_RegionOpening, &ho_RegionErosion, 7, 7);

			FillUp(ho_RegionErosion, &ho_RegionTb);

			ReduceObjectModel3dByView(ho_RegionTb, hv_Om3DScene, "xyz_mapping", HTuple(), &hv_ObjectModel3DSelected);

			CopyObjectModel3d(hv_ObjectModel3DSelected, "all", &hv_ObjectModel3DAdv);

			ObjectModel3dToXyz(&ho_X1, &ho_Y1, &ho_Z1, hv_ObjectModel3DAdv, "from_xyz_map", HTuple(), HTuple());


			//气缸区域
			GenRectangle1(&ho_ROI, 691.782, 863.44, 1097.1, 1236.79);
			Intersection(ho_ROI, ho_Z1, &ho_ROI);
			FitSurfaceFirstOrder(ho_ROI, ho_Z1, "tukey", 5, 2, &hv_Alpha, &hv_Beta, &hv_Gamma);
			AreaCenter(ho_ROI, &hv_Area, &hv_Row, &hv_Column);
			GetImageSize(ho_Z1, &hv_Width, &hv_Height);
			GenImageSurfaceFirstOrder(&ho_ImageSurface, "real", hv_Alpha, hv_Beta, hv_Gamma,
				hv_Row, hv_Column, hv_Width, hv_Height);
			SubImage(ho_Z1, ho_ImageSurface, &ho_ImageSub, -1, 0);
			Threshold(ho_ImageSub, &ho_Region, 10, 100);
			FillUp(ho_Region, &ho_RegionFillUp);
			ClosingRectangle1(ho_RegionFillUp, &ho_RegionClosing, 51, 51);
			Connection(ho_RegionClosing, &ho_ConnectedRegions);
			DiameterRegion(ho_ConnectedRegions, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2,
				&hv_Diameter);
			Rectangularity(ho_ConnectedRegions, &hv_Rectangularity);

			SelectShape(ho_ConnectedRegions, &ho_SelectedRegions, (HTuple("max_diameter").Append("rectangularity")),
				"and", (HTuple(80).Append(0.7)), (HTuple(150).Append(1)));
			OpeningRectangle1(ho_SelectedRegions, &ho_RegionOpening, 5, 5);
			SmallestRectangle1(ho_RegionOpening, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			GenRectangle1(&ho_RectangleQg, hv_Row1, hv_Column1, hv_Row2, hv_Column2);



			//子区域划分

			SmallestRectangle1(ho_RegionTb, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);

			GenRectangle1(&ho_RectangleL, hv_Row1 - 100, hv_Column1 - 100, hv_Row2 + 100, hv_Column1 + 200);
			GenRectangle1(&ho_RectangleR, hv_Row1 - 100, hv_Column2 - 200, hv_Row2 + 100, hv_Column2 + 100);
			GenRectangle1(&ho_RectangleU, hv_Row1 - 100, hv_Column1 - 100, hv_Row1 + 150, hv_Column2 + 100);
			GenRectangle1(&ho_RectangleD, hv_Row2 - 150, hv_Column1 - 100, hv_Row2 + 100, hv_Column2 + 100);

			HalconCpp::Difference(ho_RectangleU, ho_RectangleL, &ho_RegionDifference);
			HalconCpp::Difference(ho_RegionDifference, ho_RectangleR, &ho_RectangleU);
			HalconCpp::Difference(ho_RectangleD, ho_RectangleL, &ho_RegionDifference);
			HalconCpp::Difference(ho_RegionDifference, ho_RectangleR, &ho_RectangleD);



			HalconCpp::Intersection(ho_RectangleL, ho_RectangleQg, &ho_RectangleQgL);
			HalconCpp::Intersection(ho_RectangleR, ho_RectangleQg, &ho_RectangleQgR);
			HalconCpp::Intersection(ho_RectangleU, ho_RectangleQg, &ho_RectangleQgU);
			HalconCpp::Intersection(ho_RectangleD, ho_RectangleQg, &ho_RectangleQgD);





			hv_fQgOffsetL = /*25*/spara1.fQgOffsetL;
			hv_fQgOffsetR = /*25*/spara1.fQgOffsetR;
			hv_fQgOffsetU =/* 25*/spara1.fQgOffsetU;
			hv_fQgOffsetD = /*25*/spara1.fQgOffsetD;


			SmallestRectangle1(ho_RectangleQgL, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			hv_ColumnL = hv_Column2 + hv_fQgOffsetL;
			SmallestRectangle1(ho_RectangleL, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			GenRectangle1(&ho_RectangleLAdv, hv_Row1, hv_Column1, hv_Row2, hv_ColumnL);

			SmallestRectangle1(ho_RectangleQgR, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			hv_ColumnR = hv_Column1 - hv_fQgOffsetR;
			SmallestRectangle1(ho_RectangleR, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			GenRectangle1(&ho_RectangleRAdv, hv_Row1, hv_ColumnR, hv_Row2, hv_Column2);

			SmallestRectangle1(ho_RectangleQgU, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			hv_RowU = hv_Row2 + hv_fQgOffsetU;
			SmallestRectangle1(ho_RectangleU, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			GenRectangle1(&ho_RectangleUAdv, hv_Row1, hv_ColumnL, hv_RowU, hv_ColumnR);

			SmallestRectangle1(ho_RectangleQgD, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			hv_RowD = hv_Row1 - hv_fQgOffsetD;
			SmallestRectangle1(ho_RectangleD, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			GenRectangle1(&ho_RectangleDAdv, hv_RowD, hv_ColumnL, hv_Row2, hv_ColumnR);


			GenRectangle1(&ho_RectangleCAdv, hv_RowU, hv_ColumnL, hv_RowD, hv_ColumnR);

			GenEmptyObj(&ho_RectanglePartList);
			ConcatObj(ho_RectanglePartList, ho_RectangleCAdv, &ho_RectanglePartList);
			ConcatObj(ho_RectanglePartList, ho_RectangleLAdv, &ho_RectanglePartList);
			ConcatObj(ho_RectanglePartList, ho_RectangleRAdv, &ho_RectanglePartList);
			ConcatObj(ho_RectanglePartList, ho_RectangleUAdv, &ho_RectanglePartList);
			ConcatObj(ho_RectanglePartList, ho_RectangleDAdv, &ho_RectanglePartList);




			//气缸排序
			GenEmptyObj(&ho_RectangleQgSort);
			Connection(ho_RectangleQgU, &ho_ConnectedRegions);
			SortRegion(ho_ConnectedRegions, &ho_SortedRegions, "first_point", "false", "column");
			ConcatObj(ho_RectangleQgSort, ho_SortedRegions, &ho_RectangleQgSort);

			Connection(ho_RectangleQgL, &ho_ConnectedRegions);
			SortRegion(ho_ConnectedRegions, &ho_SortedRegions, "first_point", "true", "row");
			ConcatObj(ho_RectangleQgSort, ho_SortedRegions, &ho_RectangleQgSort);


			Connection(ho_RectangleQgD, &ho_ConnectedRegions);
			SortRegion(ho_ConnectedRegions, &ho_SortedRegions, "first_point", "true", "column");
			ConcatObj(ho_RectangleQgSort, ho_SortedRegions, &ho_RectangleQgSort);

			Connection(ho_RectangleQgR, &ho_ConnectedRegions);
			SortRegion(ho_ConnectedRegions, &ho_SortedRegions, "first_point", "false", "row");
			ConcatObj(ho_RectangleQgSort, ho_SortedRegions, &ho_RectangleQgSort);


			//气缸排序2
			GenEmptyObj(&ho_RectangleQgSort);
			GenEmptyObj(&ho_RegionQgReal);
			ConcatObj(ho_RegionQgReal, ho_RectangleQgU, &ho_RegionQgReal);
			ConcatObj(ho_RegionQgReal, ho_RectangleQgR, &ho_RegionQgReal);
			ConcatObj(ho_RegionQgReal, ho_RectangleQgD, &ho_RegionQgReal);
			ConcatObj(ho_RegionQgReal, ho_RectangleQgL, &ho_RegionQgReal);

			CountObj(ho_RegionQgIn, &hv_Number1);
			CountObj(ho_RegionQgReal, &hv_Number2);
			{
				HTuple end_val390 = hv_Number1;
				HTuple step_val390 = 1;
				for (hv_i = 1; hv_i.Continue(end_val390, step_val390); hv_i += step_val390)
				{
					SelectObj(ho_RegionQgIn, &ho_ObjectSelected1, hv_i);

					hv_bFind = 0;
					{
						HTuple end_val394 = hv_Number2;
						HTuple step_val394 = 1;
						for (hv_j = 1; hv_j.Continue(end_val394, step_val394); hv_j += step_val394)
						{
							SelectObj(ho_RegionQgReal, &ho_ObjectSelected2, hv_j);

							Intersection(ho_ObjectSelected2, ho_ObjectSelected1, &ho_RegionIntersection
							);
							AreaCenter(ho_RegionIntersection, &hv_Area, &hv_Row, &hv_Column);
							if (0 != (int(hv_Area > 100)))
							{
								hv_bFind = 1;
								ConcatObj(ho_RectangleQgSort, ho_ObjectSelected1, &ho_RectangleQgSort);
								break;
							}


						}
					}

					if (0 != (int(hv_bFind == 0)))
					{
						GenEmptyRegion(&ho_EmptyRegion);
						ConcatObj(ho_RectangleQgSort, ho_EmptyRegion, &ho_RectangleQgSort);
					}


				}
			}



			//***************************************************************************************************
			//step2  得到整版的粒子高度分布图
			//提取粒子高度区域 包含气缸 分区提取



			GetImageSize(ho_Z1, &hv_Width, &hv_Height);
			GenImageConst(&ho_ImageSubZ1, "real", hv_Width, hv_Height);
			GenImageConst(&ho_ImageZ1ZeroReal, "real", hv_Width, hv_Height);

			//中间区域粒子提取
			ReduceObjectModel3dByView(ho_RectangleCAdv, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DC);
			SampleObjectModel3d(hv_Om3DC, "fast", 5, HTuple(), HTuple(), &hv_SampledObjectModel3D);
			CopyObjectModel3d(hv_SampledObjectModel3D, "all", &hv_OM3DPlane);
			hv_ParFitting.Clear();
			hv_ParFitting[0] = "primitive_type";
			hv_ParFitting[1] = "fitting_algorithm";
			hv_ValFitting.Clear();
			hv_ValFitting[0] = "plane";
			hv_ValFitting[1] = "least_squares_tukey";

			FitPrimitivesObjectModel3d(hv_OM3DPlane, hv_ParFitting, hv_ValFitting, &hv_ObjectModel3DOutID);
			GetObjectModel3dParams(hv_ObjectModel3DOutID, "primitive_pose", &hv_GenParamPosePlane);
			GenPlaneObjectModel3d(hv_GenParamPosePlane, (((HTuple(-1).Append(-1)).Append(1)).Append(1)) * 900,
				(((HTuple(-1).Append(1)).Append(1)).Append(-1)) * 900, &hv_PlaneDatum);


			trans_pose_face_x(hv_GenParamPosePlane, 0, &hv_PoseTbC);

			PoseInvert(hv_PoseTbC, &hv_PoseInvert);
			PoseToHomMat3d(hv_PoseInvert, &hv_HomMat3D);
			AffineTransObjectModel3d(hv_Om3DC, hv_HomMat3D, &hv_OM3dPZeroC);

			ObjectModel3dToXyz(&ho_X1PZeroC, &ho_Y1PZeroC, &ho_Z1PZeroC, hv_OM3dPZeroC, "from_xyz_map", HTuple(), HTuple());


			//用中间区域的调平矩阵调平整个面板
			AffineTransObjectModel3d(hv_ObjectModel3DAdv, hv_HomMat3D, &hv_OM3dPZero);
			ObjectModel3dToXyz(&ho_X1PZero, &ho_Y1PZero, &ho_Z1PZero, hv_OM3dPZero, "from_xyz_map", HTuple(), HTuple());

			hv_fThBulgeLower = /*1.5*/spara1.fThBulgeLower;
			hv_fThBulgeHiger =/* 3*/spara1.fThBulgeHiger;


			GenEmptyObj(&ho_RegionRoiCBulge);
			get_plane_ranger_z_out_region_x(ho_Z1PZeroC, &ho_RegionRoiCBulge, &ho_ImageSubC, &ho_ZZeroRealC, hv_fThBulgeLower, hv_fThBulgeHiger, 50, 61, 61, 41);
			Union1(ho_RegionRoiCBulge, &ho_RegionRoiCBulgeUnion);
			GetRegionPoints(ho_RegionRoiCBulgeUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubC, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
			GetGrayval(ho_ZZeroRealC, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);

			//气缸区域粒子提取-L
			hv_fQgHOrg = /*18.0*/spara1.fQgHOrg;
			hv_fQgExCol = /*15*/spara1.fQgExCol;
			hv_fQgExRow = /*9*/spara1.fQgExRow;
			hv_fQgThOffset = /*3*/spara1.fQgThOffset;
			ReduceObjectModel3dByView(ho_RectangleLAdv, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DL);
			DilationRectangle1(ho_RectangleQg, &ho_RectangleQgEx, hv_fQgExCol, hv_fQgExRow);
			Difference(ho_RectangleLAdv, ho_RectangleQgEx, &ho_RectangleLAdvRemoveQg);
			ReduceObjectModel3dByView(ho_RectangleLAdvRemoveQg, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DLRemoveQg);

			PoseInvert(hv_PoseTbC, &hv_PoseInvert);
			PoseToHomMat3d(hv_PoseInvert, &hv_HomMat3D);
			AffineTransObjectModel3d(hv_Om3DL, hv_HomMat3D, &hv_OM3dPZeroL);
			ObjectModel3dToXyz(&ho_X1PZeroL, &ho_Y1PZeroL, &ho_Z1PZeroL, hv_OM3dPZeroL, "from_xyz_map", HTuple(), HTuple());

			Difference(ho_Z1PZeroL, ho_RectangleQgEx, &ho_RegionDifference);
			ReduceDomain(ho_Z1PZeroL, ho_RegionDifference, &ho_Z1PZeroLRemoveQg);
			Intersection(ho_Z1PZeroL, ho_RectangleQgEx, &ho_RegionQgExL);

			GenEmptyObj(&ho_RegionRoiLBulgeRemoveQg);
			get_plane_ranger_z_out_region_x(ho_Z1PZeroLRemoveQg, &ho_RegionRoiLBulgeRemoveQg,
				&ho_ImageSubLRemoveQg, &ho_ZZeroRealL, hv_fThBulgeLower, hv_fThBulgeHiger,
				50, 61, 61, 41);

			Union1(ho_RegionRoiLBulgeRemoveQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubLRemoveQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
			GetGrayval(ho_ZZeroRealL, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);

			GenEmptyObj(&ho_RegionRoiLBulgeQg);
			get_qg_z_out_region_x(ho_Z1PZeroL, ho_RegionQgExL, &ho_ImageSubLQg, &ho_RegionRoiLBulgeQg, &ho_ZZeroRealLQg, hv_fQgHOrg, hv_fQgThOffset, 100);

			Union1(ho_RegionRoiLBulgeQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubLQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);

			GetGrayval(ho_ZZeroRealLQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);




			//气缸区域粒子提取-R


			ReduceObjectModel3dByView(ho_RectangleRAdv, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DR);
			Intersection(ho_RectangleQg, ho_RectangleRAdv, &ho_RegionIntersection);

			MoveRegion(ho_RegionIntersection, &ho_RegionMoved, 0, 20);
			Union2(ho_RegionIntersection, ho_RegionMoved, &ho_RectangleQgEx);
			DilationRectangle1(ho_RectangleQgEx, &ho_RectangleQgEx, hv_fQgExCol, hv_fQgExRow);
			Difference(ho_RectangleRAdv, ho_RectangleQgEx, &ho_RectangleRAdvRemoveQg);
			ReduceObjectModel3dByView(ho_RectangleRAdvRemoveQg, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DRRemoveQg);



			PoseInvert(hv_PoseTbC, &hv_PoseInvert);
			PoseToHomMat3d(hv_PoseInvert, &hv_HomMat3D);
			AffineTransObjectModel3d(hv_Om3DR, hv_HomMat3D, &hv_OM3dPZeroR);
			ObjectModel3dToXyz(&ho_X1PZeroR, &ho_Y1PZeroR, &ho_Z1PZeroR, hv_OM3dPZeroR, "from_xyz_map", HTuple(), HTuple());


			Difference(ho_Z1PZeroR, ho_RectangleQgEx, &ho_RegionDifference);
			ReduceDomain(ho_Z1PZeroR, ho_RegionDifference, &ho_Z1PZeroRRemoveQg);
			Intersection(ho_Z1PZeroR, ho_RectangleQgEx, &ho_RegionQgExR);

			GenEmptyObj(&ho_RegionRoiRBulgeRemoveQg);
			get_plane_ranger_z_out_region_x(ho_Z1PZeroRRemoveQg, &ho_RegionRoiRBulgeRemoveQg, &ho_ImageSubRRemoveQg, &ho_ZZeroRealR, hv_fThBulgeLower, hv_fThBulgeHiger, 50, 61, 61, 41);


			Union1(ho_RegionRoiRBulgeRemoveQg, &ho_RegionUnion);

			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);

			GetGrayval(ho_ImageSubRRemoveQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
			GetGrayval(ho_ZZeroRealR, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);

			GenEmptyObj(&ho_RegionRoiRBulgeQg);
			get_qg_z_out_region_x(ho_Z1PZeroR, ho_RegionQgExR, &ho_ImageSubRQg, &ho_RegionRoiRBulgeQg, &ho_ZZeroRealRQg, hv_fQgHOrg, hv_fQgThOffset, 100);

			Union1(ho_RegionRoiRBulgeQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubRQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);

			GetGrayval(ho_ZZeroRealRQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);


			//气缸区域粒子提取-U
			ReduceObjectModel3dByView(ho_RectangleUAdv, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DU);
			DilationRectangle1(ho_RectangleQg, &ho_RectangleQgEx, hv_fQgExRow, hv_fQgExCol);
			Difference(ho_RectangleUAdv, ho_RectangleQgEx, &ho_RectangleUAdvRemoveQg);
			ReduceObjectModel3dByView(ho_RectangleUAdvRemoveQg, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DURemoveQg);


			PoseInvert(hv_PoseTbC, &hv_PoseInvert);
			PoseToHomMat3d(hv_PoseInvert, &hv_HomMat3D);
			AffineTransObjectModel3d(hv_Om3DU, hv_HomMat3D, &hv_OM3dPZeroU);
			ObjectModel3dToXyz(&ho_X1PZeroU, &ho_Y1PZeroU, &ho_Z1PZeroU, hv_OM3dPZeroU, "from_xyz_map", HTuple(), HTuple());

			Difference(ho_Z1PZeroU, ho_RectangleQgEx, &ho_RegionDifference);
			ReduceDomain(ho_Z1PZeroU, ho_RegionDifference, &ho_Z1PZeroURemoveQg);
			Intersection(ho_Z1PZeroU, ho_RectangleQgEx, &ho_RegionQgExU);


			GenEmptyObj(&ho_RegionRoiUBulgeRemoveQg);
			get_plane_ranger_z_out_region_x(ho_Z1PZeroURemoveQg, &ho_RegionRoiUBulgeRemoveQg,
				&ho_ImageSubURemoveQg, &ho_ZZeroRealU, hv_fThBulgeLower, hv_fThBulgeHiger,
				50, 61, 61, 41);
			Union1(ho_RegionRoiUBulgeRemoveQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubURemoveQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
			GetGrayval(ho_ZZeroRealU, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);


			GenEmptyObj(&ho_RegionRoiUBulgeQg);
			get_qg_z_out_region_x(ho_Z1PZeroU, ho_RegionQgExU, &ho_ImageSubUQg, &ho_RegionRoiUBulgeQg,
				&ho_ZZeroRealUQg, hv_fQgHOrg, hv_fQgThOffset, 100);



			Union1(ho_RegionRoiUBulgeQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);

			GetGrayval(ho_ImageSubUQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);


			GetGrayval(ho_ZZeroRealUQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);


			//气缸区域粒子提取-D

			ReduceObjectModel3dByView(ho_RectangleDAdv, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DD);

			DilationRectangle1(ho_RectangleQg, &ho_RectangleQgEx, hv_fQgExRow, hv_fQgExCol);

			Difference(ho_RectangleDAdv, ho_RectangleQgEx, &ho_RectangleDAdvRemoveQg);
			ReduceObjectModel3dByView(ho_RectangleDAdvRemoveQg, hv_ObjectModel3DAdv, "xyz_mapping", HTuple(), &hv_Om3DDRemoveQg);


			PoseInvert(hv_PoseTbC, &hv_PoseInvert);
			PoseToHomMat3d(hv_PoseInvert, &hv_HomMat3D);
			AffineTransObjectModel3d(hv_Om3DD, hv_HomMat3D, &hv_OM3dPZeroD);
			ObjectModel3dToXyz(&ho_X1PZeroD, &ho_Y1PZeroD, &ho_Z1PZeroD, hv_OM3dPZeroD, "from_xyz_map", HTuple(), HTuple());


			Difference(ho_Z1PZeroD, ho_RectangleQgEx, &ho_RegionDifference);
			ReduceDomain(ho_Z1PZeroD, ho_RegionDifference, &ho_Z1PZeroDRemoveQg);
			Intersection(ho_Z1PZeroD, ho_RectangleQgEx, &ho_RegionQgExD);

			GenEmptyObj(&ho_RegionRoiDBulgeRemoveQg);
			get_plane_ranger_z_out_region_x(ho_Z1PZeroDRemoveQg, &ho_RegionRoiDBulgeRemoveQg,
				&ho_ImageSubDRemoveQg, &ho_ZZeroRealD, hv_fThBulgeLower, hv_fThBulgeHiger,
				50, 61, 61, 41);

			Union1(ho_RegionRoiDBulgeRemoveQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubDRemoveQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
			GetGrayval(ho_ZZeroRealD, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);


			GenEmptyObj(&ho_RegionRoiDBulgeQg);
			get_qg_z_out_region_x(ho_Z1PZeroD, ho_RegionQgExD, &ho_ImageSubDQg, &ho_RegionRoiDBulgeQg,
				&ho_ZZeroRealDQg, hv_fQgHOrg, hv_fQgThOffset, 100);



			Union1(ho_RegionRoiDBulgeQg, &ho_RegionUnion);
			GetRegionPoints(ho_RegionUnion, &hv_Rows, &hv_Columns);
			GetGrayval(ho_ImageSubDQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);

			GetGrayval(ho_ZZeroRealDQg, hv_Rows, hv_Columns, &hv_Grayval);
			SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);


			//气缸区域合并一下
			GenEmptyObj(&ho_RegionRoiLBulge);
			ConcatObj(ho_RegionRoiLBulge, ho_RegionRoiLBulgeRemoveQg, &ho_RegionRoiLBulge
			);
			ConcatObj(ho_RegionRoiLBulge, ho_RegionRoiLBulgeQg, &ho_RegionRoiLBulge);

			GenEmptyObj(&ho_RegionRoiRBulge);
			ConcatObj(ho_RegionRoiRBulge, ho_RegionRoiRBulgeRemoveQg, &ho_RegionRoiRBulge
			);
			ConcatObj(ho_RegionRoiRBulge, ho_RegionRoiRBulgeQg, &ho_RegionRoiRBulge);


			GenEmptyObj(&ho_RegionRoiUBulge);
			ConcatObj(ho_RegionRoiUBulge, ho_RegionRoiUBulgeRemoveQg, &ho_RegionRoiUBulge
			);
			ConcatObj(ho_RegionRoiUBulge, ho_RegionRoiUBulgeQg, &ho_RegionRoiUBulge);

			GenEmptyObj(&ho_RegionRoiDBulge);
			ConcatObj(ho_RegionRoiDBulge, ho_RegionRoiDBulgeRemoveQg, &ho_RegionRoiDBulge
			);
			ConcatObj(ho_RegionRoiDBulge, ho_RegionRoiDBulgeQg, &ho_RegionRoiDBulge);


			//区域聚类合并 矩形化

			hv_fConnectionDis = /*50*/spara1.fConnectionDis;


			//非气缸区域
			connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiCBulge, &ho_RegionPartLzC, &ho_RectPartLzC, hv_fConnectionDis);

			//气缸区域
			//采用合并后的气缸区域一起进行离散分割

			connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiLBulge, &ho_RegionPartLzL, &ho_RectPartLzL, hv_fConnectionDis);

			connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiRBulge, &ho_RegionPartLzR, &ho_RectPartLzR, hv_fConnectionDis);

			connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiUBulge, &ho_RegionPartUzL, &ho_RectPartLzU, hv_fConnectionDis);

			connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiDBulge, &ho_RegionPartLzD, &ho_RectPartLzD, hv_fConnectionDis);



			//结果数据

			spara2.bTJG = true;

			spara2.PoseTb = HTuple(hv_PoseTbC);


			if (ho_X1.IsInitialized() && ho_X1.CountObj() > 0) { spara2.X1 = ho_X1.Clone(); };

			if (ho_Y1.IsInitialized() && ho_Y1.CountObj() > 0) { spara2.Y1 = ho_Y1.Clone(); };

			if (ho_Z1.IsInitialized() && ho_Z1.CountObj() > 0) { spara2.Z1 = ho_Z1.Clone(); };



			if (ho_ImageSubZ1.IsInitialized() && ho_ImageSubZ1.CountObj() > 0) { spara2.ImageSubZ1 = ho_ImageSubZ1.Clone(); };

			if (ho_ImageZ1ZeroReal.IsInitialized() && ho_ImageZ1ZeroReal.CountObj() > 0) { spara2.ImageZ1ZeroReal = ho_ImageZ1ZeroReal.Clone(); };



			if (ho_Z1PZero.IsInitialized() && ho_Z1PZero.CountObj() > 0) { spara2.Z1PZero = ho_Z1PZero.Clone(); };

			if (ho_X1PZero.IsInitialized() && ho_X1PZero.CountObj() > 0) { spara2.X1PZero = ho_X1PZero.Clone(); };

			if (ho_Y1PZeroC.IsInitialized() && ho_Y1PZero.CountObj() > 0) { spara2.Y1PZero = ho_Y1PZero.Clone(); };




			if (ho_RectPartLzC.IsInitialized() && ho_RectPartLzC.CountObj() > 0) { spara2.RectPartLzC = ho_RectPartLzC.Clone(); };


			if (ho_RectPartLzU.IsInitialized() && ho_RectPartLzU.CountObj() > 0) { spara2.RectPartLzU = ho_RectPartLzU.Clone(); };


			if (ho_RectPartLzL.IsInitialized() && ho_RectPartLzL.CountObj() > 0) { spara2.RectPartLzL = ho_RectPartLzL.Clone(); };


			if (ho_RectPartLzD.IsInitialized() && ho_RectPartLzD.CountObj() > 0) { spara2.RectPartLzD = ho_RectPartLzD.Clone(); };


			if (ho_RectPartLzR.IsInitialized() && ho_RectPartLzR.CountObj() > 0) { spara2.RectPartLzR = ho_RectPartLzR.Clone(); };


			if (ho_RectangleQgSort.IsInitialized() && ho_RectangleQgSort.CountObj() > 0) { spara2.RectangleQgSort = ho_RectangleQgSort.Clone(); };


			// 3D
			if (hv_ObjectModel3DAdv.Length() > 0)
			{
				try { CopyObjectModel3d(hv_ObjectModel3DAdv, "all", &spara2.OM3ImageAdv); }
				catch (HalconCpp::HException& ex) { ; }

			}

			sError.iCode = 0;
			sError.strInfo = "";

		}
		catch (HalconCpp::HException& ex)
		{
			//string str = ex.ToString();
			//CLogTxt.WriteTxt(str);

			sError.iCode = -1;
			sError.strInfo = "未知异常!";
		}


		break;
	}


	//释放所有临时变量

	CountSeconds(&time_end);
	spara2.time = time_end - time_start;
	return sError;
}


s_Rtnf CPlateB::OnLzPP(s_JggyPara spara1, s_DefectPlateBRtsPara spara0, s_LzppRtsPara& spara2)
{

	HTuple time_start = 0.0;
	HTuple time_end = 0.0;
	CountSeconds(&time_start);

	s_Rtnf sError;
	sError.iCode = -1;
	sError.strInfo = "";


	//复位结果数据
	spara2.Reset();



	// Local iconic variables 

	HObject ho_Domain, ho_X1, ho_Y1;
	HObject ho_Z1, ho_RectangleQgSort, ho_ImageSubZ1, ho_ImageZ1ZeroReal;
	HObject ho_Z1PZero, ho_RectPartLzC;
	HObject ho_X1PZero;
	HObject ho_Y1PZero;
	HObject ho_RectPartLzL, ho_RectPartLzR, ho_RectPartLzU;
	HObject ho_RectPartLzD, ho_RegionMxAllList, ho_XYZ1;
	HObject ho_RectPartLzCUnion, ho_RegionMxRoiListC;
	HObject ho_RegionMxRoiList, ho_RectPartLzUQgUnion;
	HObject ho_RegionMxRoiListU, ho_RectPartLzLQgUnion;
	HObject ho_RegionMxRoiListL, ho_RectPartLzDQgUnion;
	HObject ho_RegionMxRoiListD, ho_RectPartLzRQgUnion;
	HObject ho_RegionMxRoiListR, ho_ptsCross, ho_ObjectSelected;
	HObject ho_CrossSel, ho_Cross, ho_QgNotSafe;
	HObject ho_PtsQgNotSafe, ho_Arrow;
	HObject ho_ImageReduced;

	// Local control variables 

	HTuple hv_Min, hv_Max;
	HTuple hv_Range, hv_Row1;
	HTuple hv_Column1, hv_Row2;
	HTuple hv_Column2, hv_PoseTb;
	HTuple hv_HomMat3D, hv_ptsXListAll;
	HTuple hv_ptsYListAll, hv_ptsZListAll;
	HTuple hv_ptsDefListAll, hv_ptsRowListAll;
	HTuple hv_ptsColListAll, hv_fDjDiamiter;
	HTuple hv_fJgLzUpOffset, hv_fJgDpUpOffset;
	HTuple hv_iModeJgPPZStepMode, hv_fJgPPZStepFix;
	HTuple hv_fJgPPZStepK, hv_fJgPPZStepB;
	HTuple hv_iModeJgPPYStepMode, hv_fJgPPYStepFix;
	HTuple hv_fJgPPYStepK, hv_iModeJgPPSort;
	HTuple hv_fJgPPYStepCur, hv_fYResolution;
	HTuple hv_iJgPPYStepPixelCur, hv_ptsXListZeroRoiC;
	HTuple hv_ptsYListZeroRoiC, hv_ptsZListZeroRoiC;
	HTuple hv_ptsDefListZeroRoiC, hv_ptsRowListRoiC;
	HTuple hv_ptsColListRoiC, hv_ptsXListZeroRoiU;
	HTuple hv_ptsYListZeroRoiU, hv_ptsZListZeroRoiU;
	HTuple hv_ptsDefListZeroRoiU, hv_ptsRowListRoiU;
	HTuple hv_ptsColListRoiU, hv_ptsXListZeroRoiL;
	HTuple hv_ptsYListZeroRoiL, hv_ptsZListZeroRoiL;
	HTuple hv_ptsDefListZeroRoiL, hv_ptsRowListRoiL;
	HTuple hv_ptsColListRoiL, hv_ptsXListZeroRoiD;
	HTuple hv_ptsYListZeroRoiD, hv_ptsZListZeroRoiD;
	HTuple hv_ptsDefListZeroRoiD, hv_ptsRowListRoiD;
	HTuple hv_ptsColListRoiD, hv_ptsXListZeroRoiR;
	HTuple hv_ptsYListZeroRoiR, hv_ptsZListZeroRoiR;
	HTuple hv_ptsDefListZeroRoiR, hv_ptsRowListRoiR;
	HTuple hv_ptsColListRoiR, hv_ptsXList;
	HTuple hv_ptsYList, hv_ptsZList;
	HTuple hv_fQgSafeDis, hv_fResolution;
	HTuple hv_fQgSafeDisPixel, hv_ptsQgNotSafeListAll;
	HTuple hv_iNumQg, hv_iNumPts;
	HTuple /*hv_i , hv_j , */hv_IsInside;
	HTuple hv_str, hv_DistanceMin;
	HTuple hv_DistanceMax, hv_Selected;
	HTuple hv_Substrings, hv_Index;
	HTuple hv_Indices, hv_Sequence;
	HTuple hv_Reduced, hv_ptsRowListSel;
	HTuple hv_ptsColListSel, hv_Newtuple;
	HTuple hv_ptsXListAdv, hv_ptsYListAdv;
	HTuple hv_ptsZListAdv, hv_ptsDefListAdv;
	HTuple hv_ptsRowListAdv, hv_ptsColListAdv;
	HTuple hv_ptsQgNotSafeListAdv, hv_fJgTdZUp;

	HTuple hv_Area;
	HTuple hv_Row;
	HTuple hv_Column;


	// Initialize local and output iconic variables 
	GenEmptyObj(&ho_Domain);
	GenEmptyObj(&ho_X1);
	GenEmptyObj(&ho_Y1);
	GenEmptyObj(&ho_Z1);
	GenEmptyObj(&ho_RectangleQgSort);
	GenEmptyObj(&ho_ImageSubZ1);
	GenEmptyObj(&ho_ImageZ1ZeroReal);
	GenEmptyObj(&ho_Z1PZero);
	GenEmptyObj(&ho_ImageReduced);
	GenEmptyObj(&ho_RectPartLzC);
	GenEmptyObj(&ho_RectPartLzL);
	GenEmptyObj(&ho_RectPartLzR);
	GenEmptyObj(&ho_RectPartLzU);
	GenEmptyObj(&ho_RectPartLzD);
	GenEmptyObj(&ho_RegionMxAllList);
	GenEmptyObj(&ho_XYZ1);
	GenEmptyObj(&ho_RectPartLzCUnion);
	GenEmptyObj(&ho_RegionMxRoiListC);
	GenEmptyObj(&ho_RegionMxRoiList);
	GenEmptyObj(&ho_RectPartLzUQgUnion);
	GenEmptyObj(&ho_RegionMxRoiListU);
	GenEmptyObj(&ho_RectPartLzLQgUnion);
	GenEmptyObj(&ho_RegionMxRoiListL);
	GenEmptyObj(&ho_RectPartLzDQgUnion);
	GenEmptyObj(&ho_RegionMxRoiListD);
	GenEmptyObj(&ho_RectPartLzRQgUnion);
	GenEmptyObj(&ho_RegionMxRoiListR);
	GenEmptyObj(&ho_ptsCross);
	GenEmptyObj(&ho_ObjectSelected);
	GenEmptyObj(&ho_CrossSel);
	GenEmptyObj(&ho_Cross);
	GenEmptyObj(&ho_QgNotSafe);
	GenEmptyObj(&ho_PtsQgNotSafe);
	GenEmptyObj(&ho_Arrow);

	GenEmptyObj(&ho_X1PZero);
	GenEmptyObj(&ho_Y1PZero);



	while (true)
	{
		try
		{


			//判断输入
			if (!spara0.ImageSubZ1.IsInitialized() || spara0.ImageSubZ1.CountObj() == 0)
			{
				CountSeconds(&time_end);
				spara2.time = time_end - time_start;

				sError.iCode = 1;
				sError.strInfo = "图像为空!";
				break;
			}



			if (spara0.PoseTb.Length() == 0)
			{
				CountSeconds(&time_end);
				spara2.time = time_end - time_start;

				sError.iCode = 1;
				sError.strInfo = "变换矩阵异常!";
				break;
			}




			//输出中间变量
			hv_ptsXListAll = HTuple();
			hv_ptsYListAll = HTuple();
			hv_ptsZListAll = HTuple();
			hv_ptsDefListAll = HTuple();
			hv_ptsRowListAll = HTuple();
			hv_ptsColListAll = HTuple();

			GenEmptyObj(&ho_RegionMxAllList);


			//输入缺陷
			hv_PoseTb = HTuple(spara0.PoseTb);


			if (spara0.X1.IsInitialized() && spara0.X1.CountObj() > 0) { ho_X1 = spara0.X1.Clone(); };
			if (spara0.Y1.IsInitialized() && spara0.Y1.CountObj() > 0) { ho_Y1 = spara0.Y1.Clone(); };
			if (spara0.Z1.IsInitialized() && spara0.Z1.CountObj() > 0) { ho_Z1 = spara0.Z1.Clone(); };



			if (spara0.ImageSubZ1.IsInitialized() && spara0.ImageSubZ1.CountObj() > 0) { ho_ImageSubZ1 = spara0.ImageSubZ1.Clone(); };
			if (spara0.ImageZ1ZeroReal.IsInitialized() && spara0.ImageZ1ZeroReal.CountObj() > 0)
			{
				ho_ImageZ1ZeroReal = spara0.ImageZ1ZeroReal.Clone();
			};



			if (spara0.Z1PZero.IsInitialized() && spara0.Z1PZero.CountObj() > 0) { ho_Z1PZero = spara0.Z1PZero.Clone(); };
			if (spara0.X1PZero.IsInitialized() && spara0.X1PZero.CountObj() > 0) { ho_X1PZero = spara0.X1PZero.Clone(); };
			if (spara0.Y1PZero.IsInitialized() && spara0.Y1PZero.CountObj() > 0) { ho_Y1PZero = spara0.Y1PZero.Clone(); };




			if (spara0.RectPartLzC.IsInitialized() && spara0.RectPartLzC.CountObj() > 0) { ho_RectPartLzC = spara0.RectPartLzC.Clone(); };
			if (spara0.RectPartLzU.IsInitialized() && spara0.RectPartLzU.CountObj() > 0) { ho_RectPartLzU = spara0.RectPartLzU.Clone(); };
			if (spara0.RectPartLzL.IsInitialized() && spara0.RectPartLzL.CountObj() > 0) { ho_RectPartLzL = spara0.RectPartLzL.Clone(); };


			if (spara0.RectPartLzD.IsInitialized() && spara0.RectPartLzD.CountObj() > 0) { ho_RectPartLzD = spara0.RectPartLzD.Clone(); };
			if (spara0.RectPartLzR.IsInitialized() && spara0.RectPartLzR.CountObj() > 0) { ho_RectPartLzR = spara0.RectPartLzR.Clone(); };
			if (spara0.RectangleQgSort.IsInitialized() && spara0.RectangleQgSort.CountObj() > 0) { ho_RectangleQgSort = spara0.RectangleQgSort.Clone(); };




			//工艺参数输入

			hv_fDjDiamiter =/* 80.0*/spara1.fDjDiamiter;
			hv_fJgLzUpOffset = /*2*/spara1.fJgLzUpOffset;
			hv_fJgDpUpOffset = /*1.5*/spara1.fJgDpUpOffset;
			hv_iModeJgPPZStepMode = /*1*/spara1.iModeJgPPZStepMode;
			hv_fJgPPZStepFix = /*2*/spara1.fJgPPZStepFix;
			hv_fJgPPZStepK = /*0.3*/spara1.fJgPPZStepK;
			hv_fJgPPZStepB = /*1.5*/spara1.fJgPPZStepB;


			hv_iModeJgPPYStepMode = /*0*/spara1.iModeJgPPYStepMode;
			hv_fJgPPYStepFix = /*50*/spara1.fJgPPYStepFix;
			hv_fJgPPYStepK = /*0.75*/spara1.fJgPPYStepK;

			//粒子加工排序 0：从上到下 1：从下到上   2 ：从左到右  3 ：从右到左
			hv_iModeJgPPSort = /*0*/spara1.iModeJgPPSort; //该参数内部写死
			hv_fQgSafeDis =/* 50.0*/spara1.fQgSafeDis;
			hv_fJgTdZUp = /*20*/spara1.fJgTdZUp;


			//调平坐标系下路径规划-中间
			Union1(ho_RectPartLzC, &ho_RectPartLzCUnion);
			MinMaxGray(ho_RectPartLzCUnion, ho_ImageSubZ1, 0, &hv_Min, &hv_Max, &hv_Range);


			//计算当前进给Y
			hv_fJgPPYStepCur = 20;
			if (0 != (int(hv_iModeJgPPYStepMode == 0)))
			{
				hv_fJgPPYStepCur = hv_fJgPPYStepFix;
			}
			else
			{

				hv_fJgPPYStepCur = hv_fJgPPYStepK * hv_fDjDiamiter;

			}

			//计算像素分辨率

			ReduceDomain(ho_Y1, ho_RectPartLzC, &ho_ImageReduced);
			GetDomain(ho_ImageReduced, &ho_Domain);
			MinMaxGray(ho_Domain, ho_Y1, 0, &hv_Min, &hv_Max, &hv_Range);
			SmallestRectangle1(ho_Domain, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			hv_fYResolution = hv_Range / (((hv_Row1 - hv_Row2)).TupleAbs());
			hv_iJgPPYStepPixelCur = ((hv_fJgPPYStepCur / hv_fYResolution)).TupleInt()
				;
			hv_ptsXListZeroRoiC = HTuple();
			hv_ptsYListZeroRoiC = HTuple();
			hv_ptsZListZeroRoiC = HTuple();
			hv_ptsDefListZeroRoiC = HTuple();
			hv_ptsRowListRoiC = HTuple();
			hv_ptsColListRoiC = HTuple();

			hv_iModeJgPPSort = HTuple();


			hv_iModeJgPPSort = 0;
			GenEmptyObj(&ho_RegionMxRoiListC);

			cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageSubZ1, ho_ImageZ1ZeroReal, ho_RectPartLzC,
				&ho_RegionMxRoiListC, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
				hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
				&hv_ptsXListZeroRoiC, &hv_ptsYListZeroRoiC, &hv_ptsZListZeroRoiC,
				&hv_ptsDefListZeroRoiC, &hv_ptsRowListRoiC, &hv_ptsColListRoiC);



			//调平坐标系下路径规划-UP--把气缸区域和飞气缸区域直接合并 一块打磨

			Union1(ho_RectPartLzU, &ho_RectPartLzUQgUnion);
			MinMaxGray(ho_RectPartLzUQgUnion, ho_ImageSubZ1, 0, &hv_Min, &hv_Max, &hv_Range);

			//计算当前进给Y--共用
			//计算像素分辨率--共用

			hv_ptsXListZeroRoiU = HTuple();
			hv_ptsYListZeroRoiU = HTuple();
			hv_ptsZListZeroRoiU = HTuple();
			hv_ptsDefListZeroRoiU = HTuple();

			hv_ptsRowListRoiU = HTuple();

			hv_ptsColListRoiU = HTuple();

			hv_iModeJgPPSort = HTuple();
			hv_iModeJgPPSort = 3;
			GenEmptyObj(&ho_RegionMxRoiListU);

			cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzU,
				&ho_RegionMxRoiListU, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
				hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
				&hv_ptsXListZeroRoiU, &hv_ptsYListZeroRoiU, &hv_ptsZListZeroRoiU,
				&hv_ptsDefListZeroRoiU, &hv_ptsRowListRoiU, &hv_ptsColListRoiU);


			//调平坐标系下路径规划-L--把气缸区域和飞气缸区域直接合并 一块打磨



			Union1(ho_RectPartLzL, &ho_RectPartLzLQgUnion);

			MinMaxGray(ho_RectPartLzLQgUnion, ho_ImageSubZ1, 0, &hv_Min, &hv_Max, &hv_Range);

			//计算当前进给Y--共用
			//计算像素分辨率--共用

			hv_ptsXListZeroRoiL = HTuple();
			hv_ptsYListZeroRoiL = HTuple();
			hv_ptsZListZeroRoiL = HTuple();
			hv_ptsDefListZeroRoiL = HTuple();

			hv_ptsRowListRoiL = HTuple();
			hv_ptsColListRoiL = HTuple();
			hv_iModeJgPPSort = HTuple();
			hv_iModeJgPPSort = 0;

			GenEmptyObj(&ho_RegionMxRoiListL);
			cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzL,
				&ho_RegionMxRoiListL, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
				hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
				&hv_ptsXListZeroRoiL, &hv_ptsYListZeroRoiL, &hv_ptsZListZeroRoiL,
				&hv_ptsDefListZeroRoiL, &hv_ptsRowListRoiL, &hv_ptsColListRoiL);

			Union1(ho_RectPartLzD, &ho_RectPartLzDQgUnion);
			MinMaxGray(ho_RectPartLzDQgUnion, ho_ImageSubZ1, 0, &hv_Min, &hv_Max, &hv_Range);

			//计算当前进给Y--共用
			//计算像素分辨率--共用

			hv_ptsXListZeroRoiD = HTuple();
			hv_ptsYListZeroRoiD = HTuple();
			hv_ptsZListZeroRoiD = HTuple();
			hv_ptsDefListZeroRoiD = HTuple();
			hv_ptsRowListRoiD = HTuple();
			hv_ptsColListRoiD = HTuple();
			hv_iModeJgPPSort = HTuple();
			hv_iModeJgPPSort = 2;
			GenEmptyObj(&ho_RegionMxRoiListD);
			cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzD,
				&ho_RegionMxRoiListD, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
				hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
				&hv_ptsXListZeroRoiD, &hv_ptsYListZeroRoiD, &hv_ptsZListZeroRoiD,
				&hv_ptsDefListZeroRoiD, &hv_ptsRowListRoiD, &hv_ptsColListRoiD);




			//调平坐标系下路径规划-R--把气缸区域和飞气缸区域直接合并 一块打磨

			Union1(ho_RectPartLzR, &ho_RectPartLzRQgUnion);

			MinMaxGray(ho_RectPartLzRQgUnion, ho_ImageSubZ1, 0, &hv_Min, &hv_Max, &hv_Range);

			//计算当前进给Y--共用
			//计算像素分辨率--共用


			hv_ptsXListZeroRoiR = HTuple();

			hv_ptsYListZeroRoiR = HTuple();

			hv_ptsZListZeroRoiR = HTuple();

			hv_ptsDefListZeroRoiR = HTuple();


			hv_ptsRowListRoiR = HTuple();

			hv_ptsColListRoiR = HTuple();

			hv_iModeJgPPSort = 1;

			GenEmptyObj(&ho_RegionMxRoiListR);
			cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzR,
				&ho_RegionMxRoiListR, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
				hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
				&hv_ptsXListZeroRoiR, &hv_ptsYListZeroRoiR, &hv_ptsZListZeroRoiR,
				&hv_ptsDefListZeroRoiR, &hv_ptsRowListRoiR, &hv_ptsColListRoiR);


			ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListC, &ho_RegionMxAllList);
			ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListU, &ho_RegionMxAllList);
			ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListL, &ho_RegionMxAllList);
			ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListD, &ho_RegionMxAllList);
			ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListR, &ho_RegionMxAllList);



			//转换成实际坐标系下的坐标

			//中间

			PoseToHomMat3d(hv_PoseTb, &hv_HomMat3D);

			AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiC, hv_ptsYListZeroRoiC,
				hv_ptsZListZeroRoiC, &hv_ptsXList, &hv_ptsYList, &hv_ptsZList);
			hv_ptsXListAll = hv_ptsXListAll.TupleConcat(hv_ptsXList);
			hv_ptsYListAll = hv_ptsYListAll.TupleConcat(hv_ptsYList);
			hv_ptsZListAll = hv_ptsZListAll.TupleConcat(hv_ptsZList);
			hv_ptsDefListAll = hv_ptsDefListAll.TupleConcat(hv_ptsDefListZeroRoiC);
			hv_ptsRowListAll = hv_ptsRowListAll.TupleConcat(hv_ptsRowListRoiC);
			hv_ptsColListAll = hv_ptsColListAll.TupleConcat(hv_ptsColListRoiC);

			//按中-下-右-上-左顺序加工
			PoseToHomMat3d(hv_PoseTb, &hv_HomMat3D);
			AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiD, hv_ptsYListZeroRoiD, hv_ptsZListZeroRoiD,
				&hv_ptsXList, &hv_ptsYList, &hv_ptsZList);
			hv_ptsXListAll = hv_ptsXListAll.TupleConcat(hv_ptsXList);
			hv_ptsYListAll = hv_ptsYListAll.TupleConcat(hv_ptsYList);
			hv_ptsZListAll = hv_ptsZListAll.TupleConcat(hv_ptsZList);
			hv_ptsDefListAll = hv_ptsDefListAll.TupleConcat(hv_ptsDefListZeroRoiD);
			hv_ptsRowListAll = hv_ptsRowListAll.TupleConcat(hv_ptsRowListRoiD);
			hv_ptsColListAll = hv_ptsColListAll.TupleConcat(hv_ptsColListRoiD);

			PoseToHomMat3d(hv_PoseTb, &hv_HomMat3D);
			AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiR, hv_ptsYListZeroRoiR, hv_ptsZListZeroRoiR,
				&hv_ptsXList, &hv_ptsYList, &hv_ptsZList);
			hv_ptsXListAll = hv_ptsXListAll.TupleConcat(hv_ptsXList);
			hv_ptsYListAll = hv_ptsYListAll.TupleConcat(hv_ptsYList);
			hv_ptsZListAll = hv_ptsZListAll.TupleConcat(hv_ptsZList);
			hv_ptsDefListAll = hv_ptsDefListAll.TupleConcat(hv_ptsDefListZeroRoiR);
			hv_ptsRowListAll = hv_ptsRowListAll.TupleConcat(hv_ptsRowListRoiR);
			hv_ptsColListAll = hv_ptsColListAll.TupleConcat(hv_ptsColListRoiR);

			PoseToHomMat3d(hv_PoseTb, &hv_HomMat3D);
			AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiU, hv_ptsYListZeroRoiU, hv_ptsZListZeroRoiU,
				&hv_ptsXList, &hv_ptsYList, &hv_ptsZList);
			hv_ptsXListAll = hv_ptsXListAll.TupleConcat(hv_ptsXList);
			hv_ptsYListAll = hv_ptsYListAll.TupleConcat(hv_ptsYList);
			hv_ptsZListAll = hv_ptsZListAll.TupleConcat(hv_ptsZList);
			hv_ptsDefListAll = hv_ptsDefListAll.TupleConcat(hv_ptsDefListZeroRoiU);
			hv_ptsRowListAll = hv_ptsRowListAll.TupleConcat(hv_ptsRowListRoiU);
			hv_ptsColListAll = hv_ptsColListAll.TupleConcat(hv_ptsColListRoiU);



			PoseToHomMat3d(hv_PoseTb, &hv_HomMat3D);
			AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiL, hv_ptsYListZeroRoiL, hv_ptsZListZeroRoiL,
				&hv_ptsXList, &hv_ptsYList, &hv_ptsZList);
			hv_ptsXListAll = hv_ptsXListAll.TupleConcat(hv_ptsXList);
			hv_ptsYListAll = hv_ptsYListAll.TupleConcat(hv_ptsYList);
			hv_ptsZListAll = hv_ptsZListAll.TupleConcat(hv_ptsZList);
			hv_ptsDefListAll = hv_ptsDefListAll.TupleConcat(hv_ptsDefListZeroRoiL);
			hv_ptsRowListAll = hv_ptsRowListAll.TupleConcat(hv_ptsRowListRoiL);
			hv_ptsColListAll = hv_ptsColListAll.TupleConcat(hv_ptsColListRoiL);


			//气缸避位处理

			GenCrossContourXld(&ho_ptsCross, hv_ptsRowListAll, hv_ptsColListAll, 11, 0);


			//计算像素分辨率

			ReduceDomain(ho_X1, ho_RectPartLzC, &ho_ImageReduced);
			GetDomain(ho_ImageReduced, &ho_Domain);
			MinMaxGray(ho_Domain, ho_X1, 0, &hv_Min, &hv_Max, &hv_Range);
			SmallestRectangle1(ho_Domain, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
			hv_fResolution = hv_Range / (((hv_Column1 - hv_Column2)).TupleAbs());
			hv_fQgSafeDisPixel = hv_fQgSafeDis / hv_fResolution;
			TupleGenConst(hv_ptsDefListAll.TupleLength(), "", &hv_ptsQgNotSafeListAll);


			CountObj(ho_RectangleQgSort, &hv_iNumQg);
			hv_iNumPts = hv_ptsRowListAll.TupleLength();


			for (int iPts = 0; iPts < hv_iNumPts.I(); iPts++)
			{
				for (int iQg = 0; iQg < hv_iNumQg.I(); iQg++)
				{
					SelectObj(ho_RectangleQgSort, &ho_ObjectSelected, iQg + 1);

					//气缸不存在的时候 直接跳过
					AreaCenter(ho_ObjectSelected, &hv_Area, &hv_Row, &hv_Column);
					if (0 != (int(hv_Area < 100)))
					{
						continue;
					}

					SmallestRectangle1(ho_ObjectSelected, &hv_Row1, &hv_Column1, &hv_Row2, &hv_Column2);
					TestRegionPoint(ho_ObjectSelected, hv_ptsRowListAll.TupleSelect(iPts), hv_ptsColListAll.TupleSelect(iPts), &hv_IsInside);


					if (0 != (int(hv_IsInside == 1)))
					{


						if (0 != (int(HTuple(hv_ptsQgNotSafeListAll[iPts]) == HTuple(""))))
						{
							hv_ptsQgNotSafeListAll[iPts] = HTuple(iQg).TupleString("d");

						}
						else
						{
							hv_str = (HTuple(hv_ptsQgNotSafeListAll[iPts]) + HTuple(",")) + (HTuple(iQg).TupleString("d"));
							hv_ptsQgNotSafeListAll[iPts] = hv_str;

						}


						continue;

					}




					DistancePs(hv_ptsRowListAll.TupleSelect(iPts), hv_ptsColListAll.TupleSelect(
						iPts), hv_Row1, hv_Column1, hv_Row2, hv_Column2, &hv_DistanceMin,
						&hv_DistanceMax);



					if (0 != (int(hv_DistanceMin < hv_fQgSafeDisPixel)))
					{



						if (0 != (int(HTuple(hv_ptsQgNotSafeListAll[iPts]) == HTuple(""))))
						{

							hv_ptsQgNotSafeListAll[iPts] = HTuple(iQg).TupleString("d");
						}
						else
						{
							hv_str = (HTuple(hv_ptsQgNotSafeListAll[iPts]) + HTuple(",")) + (HTuple(iQg).TupleString("d"));
							hv_ptsQgNotSafeListAll[iPts] = hv_str;
						}

					}


				}



			}




			//****************************************************************************
			//点属性定义//1 起点  2 终点  3 中间点  4空跑点
			//加入空跑路径点规划

			hv_ptsXListAdv = HTuple();
			hv_ptsYListAdv = HTuple();
			hv_ptsZListAdv = HTuple();
			hv_ptsDefListAdv = HTuple();
			hv_ptsRowListAdv = HTuple();
			hv_ptsColListAdv = HTuple();
			hv_ptsQgNotSafeListAdv = HTuple();


			for (int i = 0; i <= hv_ptsDefListAll.Length() - 1; i++)
			{

				if (hv_ptsDefListAll[i].I() == 1)
				{

					hv_ptsXListAdv = (hv_ptsXListAdv.TupleConcat(HTuple(hv_ptsXListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsXListAll[HTuple(i)]));
					hv_ptsYListAdv = (hv_ptsYListAdv.TupleConcat(HTuple(hv_ptsYListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsYListAll[HTuple(i)]));
					hv_ptsZListAdv = (hv_ptsZListAdv.TupleConcat(HTuple(hv_ptsZListAll[HTuple(i)]) + 20)).TupleConcat(HTuple(hv_ptsZListAll[HTuple(i)]));
					hv_ptsDefListAdv = (hv_ptsDefListAdv.TupleConcat(4)).TupleConcat(HTuple(hv_ptsDefListAll[HTuple(i)]));
					hv_ptsRowListAdv = (hv_ptsRowListAdv.TupleConcat(HTuple(hv_ptsRowListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsRowListAll[HTuple(i)]));
					hv_ptsColListAdv = (hv_ptsColListAdv.TupleConcat(HTuple(hv_ptsColListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsColListAll[HTuple(i)]));
					hv_ptsQgNotSafeListAdv = (hv_ptsQgNotSafeListAdv.TupleConcat(HTuple(hv_ptsQgNotSafeListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsQgNotSafeListAll[HTuple(i)]));

				}

				if (hv_ptsDefListAll[i].I() == 2)
				{

					hv_ptsXListAdv = (hv_ptsXListAdv.TupleConcat(HTuple(hv_ptsXListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsXListAll[HTuple(i)]));
					hv_ptsYListAdv = (hv_ptsYListAdv.TupleConcat(HTuple(hv_ptsYListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsYListAll[HTuple(i)]));
					hv_ptsZListAdv = (hv_ptsZListAdv.TupleConcat(HTuple(hv_ptsZListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsZListAll[HTuple(i)]) + 20);
					hv_ptsDefListAdv = (hv_ptsDefListAdv.TupleConcat(HTuple(hv_ptsDefListAll[HTuple(i)]))).TupleConcat(4);
					hv_ptsRowListAdv = (hv_ptsRowListAdv.TupleConcat(HTuple(hv_ptsRowListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsRowListAll[HTuple(i)]));
					hv_ptsColListAdv = (hv_ptsColListAdv.TupleConcat(HTuple(hv_ptsColListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsColListAll[HTuple(i)]));
					hv_ptsQgNotSafeListAdv = (hv_ptsQgNotSafeListAdv.TupleConcat(HTuple(hv_ptsQgNotSafeListAll[HTuple(i)]))).TupleConcat(HTuple(hv_ptsQgNotSafeListAll[HTuple(i)]));
				}


				if (hv_ptsDefListAll[i].I() == 3)
				{


					hv_ptsXListAdv = hv_ptsXListAdv.TupleConcat(HTuple(hv_ptsXListAll[HTuple(i)]));
					hv_ptsYListAdv = hv_ptsYListAdv.TupleConcat(HTuple(hv_ptsYListAll[HTuple(i)]));
					hv_ptsZListAdv = hv_ptsZListAdv.TupleConcat(HTuple(hv_ptsZListAll[HTuple(i)]));
					hv_ptsDefListAdv = hv_ptsDefListAdv.TupleConcat(HTuple(hv_ptsDefListAll[HTuple(i)]));
					hv_ptsRowListAdv = hv_ptsRowListAdv.TupleConcat(HTuple(hv_ptsRowListAll[HTuple(i)]));
					hv_ptsColListAdv = hv_ptsColListAdv.TupleConcat(HTuple(hv_ptsColListAll[HTuple(i)]));
					hv_ptsQgNotSafeListAdv = hv_ptsQgNotSafeListAdv.TupleConcat(HTuple(hv_ptsQgNotSafeListAll[HTuple(i)]));


				}

			}



			//结果数据

			spara2.bTJG = true;


			spara2.sListPPts.clear();
			for (int i = 0; i < hv_ptsDefListAdv.Length(); i++)
			{
				s_PPts pt;

				pt.fX = hv_ptsXListAdv[i].D();
				pt.fY = hv_ptsYListAdv[i].D();
				pt.fZ = hv_ptsZListAdv[i].D();
				pt.iDef = hv_ptsDefListAdv[i].I();
				pt.fRow = hv_ptsRowListAdv[i].D();
				pt.fCol = hv_ptsColListAdv[i].D();
				pt.strQgNotSafe = hv_ptsQgNotSafeListAdv[i].S();

				spara2.sListPPts.push_back(pt);
			}

			spara2.iNumPts = hv_ptsDefListAdv.Length();


			int iNumRegion = ho_RegionMxAllList.CountObj();

			spara2.RegionMxAllList.Clear();
			if (ho_RegionMxAllList.IsInitialized() && ho_RegionMxAllList.CountObj() > 0) { spara2.RegionMxAllList = ho_RegionMxAllList.Clone(); };


			sError.iCode = 0;
			sError.strInfo = "";

		}
		catch (HalconCpp::HException& ex)
		{
			/*            string str = ex.ToString();
						CLogTxt.WriteTxt(str);*/

			sError.iCode = -1;
			sError.strInfo = "未知异常!";
		}


		break;
	}


	//释放所有临时变量

	CountSeconds(&time_end);
	spara2.time = time_end - time_start;
	return sError;
}






void CPlateB::get_plane_ranger_z_out_region_x(HObject ho_Z, HObject* ho_RegionD, HObject* ho_ZSub,
    HObject* ho_ZZeroReal, HTuple hv_ThZLower, HTuple hv_ThZHiger, HTuple hv_ThZLimit,
    HTuple hv_MaskWidth, HTuple hv_MaskHeight, HTuple hv_Expand)
{

    // Local iconic variables
    HObject  ho_Z1PZeroEx, ho_ImageMean, ho_Domain;
    HObject  ho_RegionFillUp, ho_Region1, ho_Region2, ho_ConnectedRegions;
    HObject  ho_ObjectSelected, ho_RegionIntersection, ho_ImageMeanZ;

    // Local control variables
    HTuple  hv_Number, hv_I, hv_Area, hv_Row, hv_Column;
    HTuple  hv_Grayval;


    ExpandDomainGray(ho_Z, &ho_Z1PZeroEx, hv_Expand);
    MeanImage(ho_Z1PZeroEx, &ho_ImageMean, hv_MaskWidth, hv_MaskHeight);
    SubImage(ho_ImageMean, ho_Z1PZeroEx, &(*ho_ZSub), 1, 0);

    GetDomain(ho_Z, &ho_Domain);
    FillUp(ho_Domain, &ho_RegionFillUp);
    ReduceDomain((*ho_ZSub), ho_RegionFillUp, &(*ho_ZSub));



    Threshold((*ho_ZSub), &ho_Region1, hv_ThZLower, hv_ThZLimit);
    Threshold((*ho_ZSub), &ho_Region2, hv_ThZHiger, hv_ThZLimit);
    Connection(ho_Region1, &ho_ConnectedRegions);

    GenEmptyObj(&(*ho_RegionD));

    CountObj(ho_ConnectedRegions, &hv_Number);
    {
        HTuple end_val18 = hv_Number;
        HTuple step_val18 = 1;
        for (hv_I = 1; hv_I.Continue(end_val18, step_val18); hv_I += step_val18)
        {
            SelectObj(ho_ConnectedRegions, &ho_ObjectSelected, hv_I);
            Intersection(ho_ObjectSelected, ho_Region2, &ho_RegionIntersection);
            AreaCenter(ho_RegionIntersection, &hv_Area, &hv_Row, &hv_Column);
            if (0 != (int(hv_Area > 0)))
            {
                ConcatObj((*ho_RegionD), ho_ObjectSelected, &(*ho_RegionD));
            }

        }
    }

    //额外输出一份真实的高度 Z向上为正

    MeanImage(ho_Z, &ho_ImageMeanZ, 3, 3);
    CopyImage((*ho_ZSub), &(*ho_ZZeroReal));
    CountObj((*ho_RegionD), &hv_Number);
    {
        HTuple end_val33 = hv_Number;
        HTuple step_val33 = 1;
        for (hv_I = 1; hv_I.Continue(end_val33, step_val33); hv_I += step_val33)
        {
            SelectObj(ho_ConnectedRegions, &ho_ObjectSelected, hv_I);
            GetDomain(ho_ObjectSelected, &ho_Domain);
            GetRegionPoints(ho_Domain, &hv_Row, &hv_Column);
            GetGrayval(ho_ImageMeanZ, hv_Row, hv_Column, &hv_Grayval);
            SetGrayval((*ho_ZZeroReal), hv_Row, hv_Column, -hv_Grayval);

        }
    }


    return;
}

void CPlateB::get_qg_z_out_region_x(HObject ho_Z, HObject ho_RegionQg, HObject* ho_ZSub,
    HObject* ho_RegionD, HObject* ho_ZZeroReal, HTuple hv_QgHOrg, HTuple hv_ThZOuter,
    HTuple hv_ThZlimit)
{

    // Local iconic variables
    HObject  ho_RegionFillUp, ho_ConnectedRegions;
    HObject  ho_ObjectSelected, ho_RegionDilation, ho_RegionDifference;
    HObject  ho_Domain, ho_RegionIntersection, ho_RegionOpening;
    HObject  ho_RegionErosion;

    // Local control variables
    HTuple  hv_Width, hv_Height, hv_Number, hv_I;
    HTuple  hv_MeanRef, hv_Deviation, hv_MeanMark, hv_HQg, hv_HQgLz;
    HTuple  hv_Rows, hv_Columns, hv_Newtuple, hv_HQg2, hv_HQgLz2;
    HTuple  hv_Newtuple2;




    GetImageSize(ho_Z, &hv_Width, &hv_Height);
    GenImageConst(&(*ho_ZSub), "real", hv_Width, hv_Height);
    GenImageConst(&(*ho_ZZeroReal), "real", hv_Width, hv_Height);
    GenEmptyObj(&(*ho_RegionD));



    FillUp(ho_RegionQg, &ho_RegionFillUp);

    Connection(ho_RegionFillUp, &ho_ConnectedRegions);
    CountObj(ho_ConnectedRegions, &hv_Number);
    {
        HTuple end_val14 = hv_Number;
        HTuple step_val14 = 1;
        for (hv_I = 1; hv_I.Continue(end_val14, step_val14); hv_I += step_val14)
        {
            SelectObj(ho_ConnectedRegions, &ho_ObjectSelected, hv_I);


            DilationRectangle1(ho_ObjectSelected, &ho_RegionDilation, 71, 71);
            Difference(ho_RegionDilation, ho_ObjectSelected, &ho_RegionDifference);

            GetDomain(ho_Z, &ho_Domain);
            Intersection(ho_RegionDifference, ho_Domain, &ho_RegionIntersection);
            Intensity(ho_RegionIntersection, ho_Z, &hv_MeanRef, &hv_Deviation);


            Intersection(ho_ObjectSelected, ho_Z, &ho_RegionIntersection);
            FillUp(ho_RegionIntersection, &ho_RegionFillUp);
            OpeningRectangle1(ho_RegionFillUp, &ho_RegionOpening, 5, 5);
            ErosionRectangle1(ho_RegionOpening, &ho_RegionErosion, 21, 21);

            Intersection(ho_RegionErosion, ho_Z, &ho_RegionIntersection);
            Intensity(ho_RegionIntersection, ho_Z, &hv_MeanMark, &hv_Deviation);

            hv_HQg = (hv_MeanMark - hv_MeanRef).TupleAbs();
            hv_HQgLz = hv_HQg - hv_QgHOrg;

            GetRegionPoints(ho_ObjectSelected, &hv_Rows, &hv_Columns);
            TupleGenConst(hv_Rows.TupleLength(), hv_HQgLz, &hv_Newtuple);
            SetGrayval((*ho_ZSub), hv_Rows, hv_Columns, hv_Newtuple);


            hv_HQg2 = hv_MeanMark.TupleAbs();
            hv_HQgLz2 = hv_HQg2 - hv_QgHOrg;
            TupleGenConst(hv_Rows.TupleLength(), hv_HQgLz2, &hv_Newtuple2);
            SetGrayval((*ho_ZZeroReal), hv_Rows, hv_Columns, hv_Newtuple2);

            if (0 != (HTuple(int(hv_HQgLz > hv_ThZOuter)).TupleAnd(int(hv_HQgLz < hv_ThZlimit))))
            {

                ConcatObj((*ho_RegionD), ho_ObjectSelected, &(*ho_RegionD));
            }


        }
    }

    return;
}



// Local procedures 
void CPlateB::cal_lzgj_image_pp_r1_x(HObject ho_X, HObject ho_Y, HObject ho_Z, HObject ho_ZReal,
    HObject ho_ZSub, HObject ho_RectLzs, HObject* ho_RegionMXs, HTuple hv_iModeJgPPSort,
    HTuple hv_iJgPPYStepPixel, HTuple hv_iModeJgPPZStepMode, HTuple hv_fJgPPZStepFix,
    HTuple hv_fJgPPZStepK, HTuple hv_fJgPPZStepB, HTuple hv_fJgLzUpOffset, HTuple hv_fJgDpUpOffset,
    HTuple* hv_ptsXList, HTuple* hv_ptsYList, HTuple* hv_ptsZList, HTuple* hv_ptsDefList,
    HTuple* hv_ptsRowList, HTuple* hv_ptsColList)
{

    // Local iconic variables
    HObject  ho_SortedRegions, ho_LzSelected, ho_Partitioned;
    HObject  ho_RegionMxList, ho_ObjectSelected, ho_Domain, ho_RegionIntersection;
    HObject  ho_RegionMx;

    // Local control variables
    HTuple  hv_NumLz, hv_iNumLz, hv_NumPart, hv_ptsXListZeroS;
    HTuple  hv_ptsYListZeroS, hv_ptsZListZeroS, hv_ptsDefListZeroS;
    HTuple  hv_ptsRowListS, hv_ptsColListS, hv_bOdd, hv_iPart;
    HTuple  hv_MinX, hv_MaxX, hv_Range, hv_MeanY, hv_Deviation;
    HTuple  hv_Row13, hv_Column13, hv_Row23, hv_Column23, hv_ValX1;
    HTuple  hv_ValX2, hv_ValY, hv_RowCenter, hv_ptsXListZeroM;
    HTuple  hv_ptsYListZeroM, hv_ptsZListZeroM, hv_ptsDefListZeroM;
    HTuple  hv_ptsRowListZeroM, hv_ptsColListZeroM, hv_Min;
    HTuple  hv_Max, hv_Min2, hv_Max2, hv_Range2, hv_DmZ, hv_LzHeight;
    HTuple  hv_MxHeight, hv_fMxZCur, hv_iLayer, hv_bLast, hv_fJgPPZStepCur;
    HTuple  hv_Newtuple, hv_ddd, hv_ddd2;


    (*hv_ptsXList) = HTuple();
    (*hv_ptsYList) = HTuple();
    (*hv_ptsZList) = HTuple();
    (*hv_ptsDefList) = HTuple();

    (*hv_ptsRowList) = HTuple();
    (*hv_ptsColList) = HTuple();

    GenEmptyObj(&(*ho_RegionMXs));

    if (0 != (int(hv_iModeJgPPSort == 0)))
    {

        SortRegion(ho_RectLzs, &ho_SortedRegions, "first_point", "true", "row");
    }
    else if (0 != (int(hv_iModeJgPPSort == 1)))
    {
        SortRegion(ho_RectLzs, &ho_SortedRegions, "first_point", "false", "row");
    }
    else if (0 != (int(hv_iModeJgPPSort == 2)))
    {
        SortRegion(ho_RectLzs, &ho_SortedRegions, "first_point", "true", "column");
    }
    else
    {
        SortRegion(ho_RectLzs, &ho_SortedRegions, "first_point", "false", "column");
    }

    CountObj(ho_SortedRegions, &hv_NumLz);
    {
        HTuple end_val23 = hv_NumLz - 1;
        HTuple step_val23 = 1;
        for (hv_iNumLz = 0; hv_iNumLz.Continue(end_val23, step_val23); hv_iNumLz += step_val23)
        {
            //Y方向切块 根据设置的mm进给值计算出切割像素值
            SelectObj(ho_SortedRegions, &ho_LzSelected, hv_iNumLz + 1);
            PartitionRectangle(ho_LzSelected, &ho_Partitioned, 3000, hv_iJgPPYStepPixel);

            CountObj(ho_Partitioned, &hv_NumPart);


            GenEmptyObj(&ho_RegionMxList);
            hv_ptsXListZeroS = HTuple();
            hv_ptsYListZeroS = HTuple();
            hv_ptsZListZeroS = HTuple();
            hv_ptsDefListZeroS = HTuple();

            hv_ptsRowListS = HTuple();
            hv_ptsColListS = HTuple();

            hv_bOdd = 0;

            {
                HTuple end_val42 = hv_NumPart - 1;
                HTuple step_val42 = 1;
                for (hv_iPart = 0; hv_iPart.Continue(end_val42, step_val42); hv_iPart += step_val42)
                {

                    SelectObj(ho_Partitioned, &ho_ObjectSelected, hv_iPart + 1);

                    GetDomain(ho_Z, &ho_Domain);
                    Intersection(ho_ObjectSelected, ho_Domain, &ho_RegionIntersection);

                    MinMaxGray(ho_RegionIntersection, ho_X, 0, &hv_MinX, &hv_MaxX, &hv_Range);
                    Intensity(ho_RegionIntersection, ho_Y, &hv_MeanY, &hv_Deviation);
                    SmallestRectangle1(ho_ObjectSelected, &hv_Row13, &hv_Column13, &hv_Row23, &hv_Column23);
                    GenRectangle1(&ho_RegionMx, hv_Row13, hv_Column13, hv_Row23, hv_Column23);

                    ConcatObj(ho_RegionMxList, ho_RegionMx, &ho_RegionMxList);


                    hv_ValX1 = hv_MinX;
                    hv_ValX2 = hv_MaxX;
                    hv_ValY = hv_MeanY;


                    hv_ptsYListZeroS = hv_ptsYListZeroS.TupleConcat(hv_ValY);
                    hv_ptsZListZeroS = hv_ptsZListZeroS.TupleConcat(0);
                    hv_ptsYListZeroS = hv_ptsYListZeroS.TupleConcat(hv_ValY);
                    hv_ptsZListZeroS = hv_ptsZListZeroS.TupleConcat(0);

                    hv_RowCenter = (hv_Row13 / 2) + (hv_Row23 / 2);
                    hv_ptsRowListS = hv_ptsRowListS.TupleConcat(hv_RowCenter);
                    hv_ptsRowListS = hv_ptsRowListS.TupleConcat(hv_RowCenter);

                    hv_bOdd = hv_iPart % 2;
                    if (0 != (int(hv_bOdd == 0)))
                    {
                        hv_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(hv_MinX);
                        hv_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(hv_MaxX);

                        hv_ptsColListS = hv_ptsColListS.TupleConcat(hv_Column13);
                        hv_ptsColListS = hv_ptsColListS.TupleConcat(hv_Column23);

                    }
                    else
                    {
                        hv_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(hv_MaxX);
                        hv_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(hv_MinX);

                        hv_ptsColListS = hv_ptsColListS.TupleConcat(hv_Column23);
                        hv_ptsColListS = hv_ptsColListS.TupleConcat(hv_Column13);

                    }

                    hv_ptsDefListZeroS = hv_ptsDefListZeroS.TupleConcat(3);
                    hv_ptsDefListZeroS = hv_ptsDefListZeroS.TupleConcat(3);


                }
            }

            //包含Z深度方向多层路径规划
            hv_ptsXListZeroM = HTuple();
            hv_ptsYListZeroM = HTuple();
            hv_ptsZListZeroM = HTuple();
            hv_ptsDefListZeroM = HTuple();

            hv_ptsRowListZeroM = HTuple();
            hv_ptsColListZeroM = HTuple();

            //粒子绝对高度
            MinMaxGray(ho_LzSelected, ho_ZReal, 0, &hv_Min, &hv_Max, &hv_Range);
            //粒子相对高度
            MinMaxGray(ho_LzSelected, ho_ZSub, 0, &hv_Min2, &hv_Max2, &hv_Range2);

            //粒子底部相对于零平面的高度
            hv_DmZ = hv_Max - hv_Max2;

            hv_LzHeight = hv_Max;
            hv_MxHeight = ((hv_LzHeight + hv_fJgLzUpOffset) - hv_fJgDpUpOffset) - hv_DmZ;

            hv_fMxZCur = hv_LzHeight;
            for (hv_iLayer = 0; hv_iLayer <= 100; hv_iLayer += 1)
            {

                hv_bLast = 0;

                //计算当前进给Z
                hv_fJgPPZStepCur = 1.0;
                if (0 != (int(hv_iModeJgPPZStepMode == 0)))
                {
                    hv_fJgPPZStepCur = hv_fJgPPZStepFix;
                }
                else
                {
                    hv_fJgPPZStepCur = (hv_fJgPPZStepK * hv_fMxZCur) + hv_fJgPPZStepB;
                }



                hv_fMxZCur = hv_fMxZCur - hv_fJgPPZStepCur;
                if (0 != (int(hv_fMxZCur < (hv_fJgDpUpOffset + hv_DmZ))))
                {
                    hv_fMxZCur = hv_fJgDpUpOffset + hv_DmZ;
                    hv_bLast = 1;
                }

                hv_ptsXListZeroM = hv_ptsXListZeroM.TupleConcat(hv_ptsXListZeroS);
                hv_ptsYListZeroM = hv_ptsYListZeroM.TupleConcat(hv_ptsYListZeroS);
                TupleGenConst(hv_ptsZListZeroS.TupleLength(), hv_fMxZCur * -1.0, &hv_Newtuple);
                hv_ptsZListZeroM = hv_ptsZListZeroM.TupleConcat(hv_Newtuple);
                hv_ptsDefListZeroM = hv_ptsDefListZeroM.TupleConcat(hv_ptsDefListZeroS);

                hv_ptsRowListZeroM = hv_ptsRowListZeroM.TupleConcat(hv_ptsRowListS);
                hv_ptsColListZeroM = hv_ptsColListZeroM.TupleConcat(hv_ptsColListS);


                if (0 != hv_bLast)
                {
                    break;
                }

            }

            hv_ptsDefListZeroM[0] = 1;
            hv_ptsDefListZeroM[(hv_ptsDefListZeroM.TupleLength()) - 1] = 2;



            //添加到区域

            (*hv_ptsXList) = (*hv_ptsXList).TupleConcat(hv_ptsXListZeroM);
            (*hv_ptsYList) = (*hv_ptsYList).TupleConcat(hv_ptsYListZeroM);
            (*hv_ptsZList) = (*hv_ptsZList).TupleConcat(hv_ptsZListZeroM);
            (*hv_ptsDefList) = (*hv_ptsDefList).TupleConcat(hv_ptsDefListZeroM);


            (*hv_ptsRowList) = (*hv_ptsRowList).TupleConcat(hv_ptsRowListZeroM);
            (*hv_ptsColList) = (*hv_ptsColList).TupleConcat(hv_ptsColListZeroM);

            ConcatObj((*ho_RegionMXs), ho_RegionMxList, &(*ho_RegionMXs));

            hv_ddd = 0;

        }
    }


    hv_ddd2 = 0;

    return;
}


void  CPlateB:: trans_pose_face_x(HTuple hv_Pose1, HTuple hv_bFaceOrg, HTuple* hv_Pose2)
{

    // Local iconic variables

    // Local control variables
    HTuple  hv_PlaneDatum, hv_SampledObjectModel3D;
    HTuple  hv_ObjectModel3DNormals, hv_valNx, hv_valNy, hv_valNz;
    HTuple  hv_ValCosX, hv_ValCosY, hv_ValCosZ, hv_OriginX;
    HTuple  hv_OriginY, hv_OriginZ, hv_TargetX, hv_TargetY;
    HTuple  hv_TargetZ, hv_HomMat3D;





    GenPlaneObjectModel3d(hv_Pose1, (((HTuple(-1).Append(-1)).Append(1)).Append(1)) * 50,
        (((HTuple(-1).Append(1)).Append(1)).Append(-1)) * 50, &hv_PlaneDatum);

    SampleObjectModel3d(hv_PlaneDatum, "fast", 5, HTuple(), HTuple(), &hv_SampledObjectModel3D);
    SurfaceNormalsObjectModel3d(hv_SampledObjectModel3D, "mls", "mls_force_inwards",
        "true", &hv_ObjectModel3DNormals);
    //visualize_object_model_3d (WindowHandle, [ObjectModel3DNormals], [], [], [ 'lut','color_attrib','normal_color','point_size','disp_normals','disp_pose'], ['color1','coord_z','white',16,'true','true'], [], [], [], Pose2)


    GetObjectModel3dParams(hv_ObjectModel3DNormals, "point_normal_x", &hv_valNx);
    GetObjectModel3dParams(hv_ObjectModel3DNormals, "point_normal_y", &hv_valNy);
    GetObjectModel3dParams(hv_ObjectModel3DNormals, "point_normal_z", &hv_valNz);


    //平面拟合后的法向是朝向原点的 】

    if (0 != hv_bFaceOrg)
    {

        TupleMean(hv_valNx, &hv_ValCosX);
        TupleMean(hv_valNy, &hv_ValCosY);
        TupleMean(hv_valNz, &hv_ValCosZ);

    }
    else
    {


        TupleMean(-hv_valNx, &hv_ValCosX);
        TupleMean(-hv_valNy, &hv_ValCosY);
        TupleMean(-hv_valNz, &hv_ValCosZ);
    }





    hv_OriginX.Clear();
    hv_OriginX[0] = 0;
    hv_OriginX[1] = 0;
    hv_OriginX[2] = 0;
    hv_OriginY.Clear();
    hv_OriginY[0] = 0;
    hv_OriginY[1] = 0;
    hv_OriginY[2] = 0;
    hv_OriginZ.Clear();
    hv_OriginZ[0] = 0;
    hv_OriginZ[1] = 0.5;
    hv_OriginZ[2] = 1;
    hv_TargetX.Clear();
    hv_TargetX[0] = 0;
    hv_TargetX.Append(hv_ValCosX / 2);
    hv_TargetX.Append(hv_ValCosX);
    hv_TargetY.Clear();
    hv_TargetY[0] = 0;
    hv_TargetY.Append(hv_ValCosY / 2);
    hv_TargetY.Append(hv_ValCosY);
    hv_TargetZ.Clear();
    hv_TargetZ[0] = 0;
    hv_TargetZ.Append(hv_ValCosZ / 2);
    hv_TargetZ.Append(hv_ValCosZ);


    VectorToHomMat3d("rigid", hv_OriginX, hv_OriginY, hv_OriginZ, hv_TargetX, hv_TargetY,
        hv_TargetZ, &hv_HomMat3D);
    HomMat3dToPose(hv_HomMat3D, &(*hv_Pose2));

    (*hv_Pose2)[0] = HTuple(hv_Pose1[0]);
    (*hv_Pose2)[1] = HTuple(hv_Pose1[1]);
    (*hv_Pose2)[2] = HTuple(hv_Pose1[2]);

    (*hv_Pose2)[5] = 0;
    //gen_arrow_object_model_3d_x (2, 500, Pose1, OM3DArrow2)
    //visualize_object_model_3d (WindowHandle, [PlaneDatum,OM3DArrow2], [], [], ['lut','color_attrib','disp_pose'], ['color1','coord_z','true'], [], [], [], Pose2)

    ClearObjectModel3d(hv_PlaneDatum);
    ClearObjectModel3d(hv_SampledObjectModel3D);
    ClearObjectModel3d(hv_ObjectModel3DNormals);


    return;
}


void CPlateB:: connection_3d_region_by_dis_x(HObject ho_X, HObject ho_Y, HObject ho_Z, HObject ho_Region,
    HObject* ho_RegionPart, HObject* ho_RectPart, HTuple hv_Dis)
{

    // Local iconic variables
    HObject  ho_RegionUnion, ho_ImageReduced, ho_XLz;
    HObject  ho_YLz, ho_ZLz, ho_Domain;

    // Local control variables
    HTuple  hv_OM3dLz, hv_ObjectModel3DConnected;
    HTuple  hv_i, hv_Number, hv_Row11, hv_Column11, hv_Row2;
    HTuple  hv_Column2;


    GenEmptyObj(&(*ho_RegionPart));
    GenEmptyObj(&(*ho_RectPart));

    Union1(ho_Region, &ho_RegionUnion);
    ReduceDomain(ho_Z, ho_RegionUnion, &ho_ImageReduced);

    XyzToObjectModel3d(ho_X, ho_Y, ho_ImageReduced, &hv_OM3dLz);
    ConnectionObjectModel3d(hv_OM3dLz, "distance_3d", hv_Dis, &hv_ObjectModel3DConnected);


    {
        HTuple end_val11 = (hv_ObjectModel3DConnected.TupleLength()) - 1;
        HTuple step_val11 = 1;
        for (hv_i = 0; hv_i.Continue(end_val11, step_val11); hv_i += step_val11)
        {
            ObjectModel3dToXyz(&ho_XLz, &ho_YLz, &ho_ZLz, HTuple(hv_ObjectModel3DConnected[hv_i]),
                "from_xyz_map", HTuple(), HTuple());

            GetDomain(ho_XLz, &ho_Domain);
            ConcatObj((*ho_RegionPart), ho_Domain, &(*ho_RegionPart));

        }
    }

    CountObj((*ho_RegionPart), &hv_Number);
    if (0 != (int(hv_Number > 0)))
    {
        SmallestRectangle1((*ho_RegionPart), &hv_Row11, &hv_Column11, &hv_Row2, &hv_Column2);
        GenRectangle1(&(*ho_RectPart), hv_Row11, hv_Column11, hv_Row2, hv_Column2);

    }

    return;
}
