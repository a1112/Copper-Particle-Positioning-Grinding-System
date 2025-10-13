
#include "pch.h"

#include "CHVisionAdvX.h"

CHVisionAdvX::CHVisionAdvX()
{
}


CHVisionAdvX::~CHVisionAdvX()
{
}


bool CHVisionAdvX::is_directory_exists(const std::string& path)
{
    DWORD attrib = GetFileAttributesA(path.c_str());

    // 检查路径的有效性以及是否为目录
    return (attrib != INVALID_FILE_ATTRIBUTES && (attrib & FILE_ATTRIBUTE_DIRECTORY));
}

bool CHVisionAdvX::is_file_exists(const std::string& path) {
    DWORD attrib = GetFileAttributesA(path.c_str());

    // 检查路径是否有效且不是一个目录
    return (attrib != INVALID_FILE_ATTRIBUTES && !(attrib & FILE_ATTRIBUTE_DIRECTORY));
}

int CHVisionAdvX::ReadImage3DX(s_Image3dS& imgTable,
    std::string sFullPathNameRemoveSuffix,  //图像全路径去掉后缀及类型
    std::string strGraySuffix ,      //灰度图后缀
    std::string strPointCloudSuffix ,  //点云后缀
    std::string strNormalSuffix     //法线后缀
)
{
    std::string sFullPathGray = sFullPathNameRemoveSuffix + strGraySuffix + ".png";


    //文件是否存在
    if (!is_file_exists(sFullPathGray))
    {
        return 1;
    }


    //读取原始图像数据
    HObject ho_X, ho_Y, ho_Z, ho_NX;
    HObject ho_NY, ho_NZ, ho_Texture, ho_GrayImage;
    HObject ho_Region;


    HTuple hv_ObjectModel3D;
    HTuple hv_Rows, hv_Columns;
    HTuple hv_NXV, hv_NYV, hv_NZV;
    HTuple hv_Intensity;
    HTuple hv_RV, hv_GV, hv_BV;

    try
    {


        ReadImage(&ho_Texture, (sFullPathNameRemoveSuffix + strGraySuffix + ".png").c_str());
        Rgb1ToGray(ho_Texture, &ho_GrayImage);
        ReadImage(&ho_X, (sFullPathNameRemoveSuffix + strPointCloudSuffix + "X.tif").c_str());
        ReadImage(&ho_Y, (sFullPathNameRemoveSuffix + strPointCloudSuffix + "Y.tif").c_str());
        ReadImage(&ho_Z, (sFullPathNameRemoveSuffix + strPointCloudSuffix + "Z.tif").c_str());


        bool bNormalExist = false;
        try
        {
            ReadImage(&ho_NX, (sFullPathNameRemoveSuffix + strNormalSuffix + "X.tif").c_str());
            ReadImage(&ho_NY, (sFullPathNameRemoveSuffix + strNormalSuffix + "Y.tif").c_str());
            ReadImage(&ho_NZ, (sFullPathNameRemoveSuffix + strNormalSuffix + "Z.tif").c_str());

            bNormalExist = true;
        }
        catch (HalconCpp::HException& ex)
        {

        }



        //生成object3D 并添加各种元素

        GetDomain(ho_Z, &ho_Region);
        GetRegionPoints(ho_Region, &hv_Rows, &hv_Columns);

        ReduceDomain(ho_GrayImage, ho_Region, &ho_GrayImage);
        ReduceDomain(ho_X, ho_Region, &ho_X);
        ReduceDomain(ho_Y, ho_Region, &ho_Y);
        ReduceDomain(ho_Z, ho_Region, &ho_Z);

        if (bNormalExist)
        {
            ReduceDomain(ho_NX, ho_Region, &ho_NX);
            ReduceDomain(ho_NY, ho_Region, &ho_NY);
            ReduceDomain(ho_NZ, ho_Region, &ho_NZ);
        }



        XyzToObjectModel3d(ho_X, ho_Y, ho_Z, &hv_ObjectModel3D);


        //强度信息

        GetGrayval(ho_GrayImage, hv_Rows, hv_Columns, &hv_Intensity);
        SetObjectModel3dAttribMod(hv_ObjectModel3D, "&intensity", "points", hv_Intensity);



        //法线信息
        HObject ho_Image1, ho_Image2;
        HObject ho_Image3, ho_ImageH, ho_ImageS;
        HObject ho_ImageV, ho_ImageR, ho_ImageG;
        HObject ho_ImageB, ho_Multichannel;

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


        if (bNormalExist)
        {

            GetGrayval(ho_NX, hv_Rows, hv_Columns, &hv_NXV);
            GetGrayval(ho_NY, hv_Rows, hv_Columns, &hv_NYV);
            GetGrayval(ho_NZ, hv_Rows, hv_Columns, &hv_NZV);


            SetObjectModel3dAttribMod(hv_ObjectModel3D, ((HTuple("point_normal_x").Append("point_normal_y")).Append("point_normal_z")),
                HTuple(), (hv_NXV.TupleConcat(hv_NYV)).TupleConcat(hv_NZV));


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


        s_Image3dS As;
        As.Gray = ho_GrayImage.Clone();
        As.X = ho_X.Clone();
        As.Y = ho_Y.Clone();
        As.Z = ho_Z.Clone();

        if (bNormalExist)
        {
            As.NX = ho_NX.Clone();
            As.NY = ho_NY.Clone();
            As.NZ = ho_NZ.Clone();
        }


        CopyObjectModel3d(hv_ObjectModel3D, "all", &As.ObjectModel3D);

        imgTable = As;

        if (hv_ObjectModel3D.Length() > 0)
        {
            ClearObjectModel3d(hv_ObjectModel3D);
        }



    }
    catch (HalconCpp::HException& ex)
    {

        return -1;
    }

    return 0;

}



int  CHVisionAdvX::WriteImage3DX(s_Image3dS imgTable, std::string szFolderPath, std::string sNameRemoveSuffix)
{

    //提取路径文件夹路径

    if (!is_directory_exists(szFolderPath))
        return 1;


    std::string   sPathNoFileType = szFolderPath + "\\" + sNameRemoveSuffix;

    try
    {

        HTuple hv_FilePathX = (sPathNoFileType + "_IMG_PointCloud_X").c_str();
        WriteImage(imgTable.X, "tiff", 0, hv_FilePathX);

        HTuple hv_FilePathY = (sPathNoFileType + "_IMG_PointCloud_Y").c_str();
        WriteImage(imgTable.Y, "tiff", 0, hv_FilePathY);

        HTuple hv_FilePathZ = (sPathNoFileType + "_IMG_PointCloud_Z").c_str();
        WriteImage(imgTable.Z, "tiff", 0, hv_FilePathZ);


        HTuple hv_FilePathNX = (sPathNoFileType + "_IMG_NormalMap_X").c_str();
        WriteImage(imgTable.NX, "tiff", 0, hv_FilePathNX);

        HTuple hv_FilePathNY = (sPathNoFileType + "_IMG_NormalMap_Y").c_str();
        WriteImage(imgTable.NY, "tiff", 0, hv_FilePathNY);

        HTuple hv_FilePathNZ = (sPathNoFileType + "_IMG_NormalMap_Z").c_str();
        WriteImage(imgTable.NZ, "tiff", 0, hv_FilePathNZ);

        HTuple hv_FilePathGray = (sPathNoFileType + "_IMG_Texture_8Bit").c_str();
        WriteImage(imgTable.Gray, "png fastest", 0, hv_FilePathGray);


    }
    catch (HalconCpp::HException& ex)
    {


        return -1;

    }

    return 0;

}



void CHVisionAdvX::gen_arrow_contour_xld(HObject* ho_Arrow, HTuple hv_Row1, HTuple hv_Column1,
    HTuple hv_Row2, HTuple hv_Column2, HTuple hv_HeadLength, HTuple hv_HeadWidth)
{

    // Local iconic variables
    HObject  ho_TempArrow;

    // Local control variables
    HTuple  hv_Length, hv_ZeroLengthIndices, hv_DR;
    HTuple  hv_DC, hv_HalfHeadWidth, hv_RowP1, hv_ColP1, hv_RowP2;
    HTuple  hv_ColP2, hv_Index;

    //This procedure generates arrow shaped XLD contours,
    //pointing from (Row1, Column1) to (Row2, Column2).
    //If starting and end point are identical, a contour consisting
    //of a single point is returned.
    //
    //input parameteres:
    //Row1, Column1: Coordinates of the arrows' starting points
    //Row2, Column2: Coordinates of the arrows' end points
    //HeadLength, HeadWidth: Size of the arrow heads in pixels
    //
    //output parameter:
    //Arrow: The resulting XLD contour
    //
    //The input tuples Row1, Column1, Row2, and Column2 have to be of
    //the same length.
    //HeadLength and HeadWidth either have to be of the same length as
    //Row1, Column1, Row2, and Column2 or have to be a single element.
    //If one of the above restrictions is violated, an error will occur.
    //
    //
    //Init
    GenEmptyObj(&(*ho_Arrow));
    //
    //Calculate the arrow length
    DistancePp(hv_Row1, hv_Column1, hv_Row2, hv_Column2, &hv_Length);
    //
    //Mark arrows with identical start and end point
    //(set Length to -1 to avoid division-by-zero exception)
    hv_ZeroLengthIndices = hv_Length.TupleFind(0);
    if (0 != (int(hv_ZeroLengthIndices != -1)))
    {
        hv_Length[hv_ZeroLengthIndices] = -1;
    }
    //
    //Calculate auxiliary variables.
    hv_DR = (1.0 * (hv_Row2 - hv_Row1)) / hv_Length;
    hv_DC = (1.0 * (hv_Column2 - hv_Column1)) / hv_Length;
    hv_HalfHeadWidth = hv_HeadWidth / 2.0;
    //
    //Calculate end points of the arrow head.
    hv_RowP1 = (hv_Row1 + ((hv_Length - hv_HeadLength) * hv_DR)) + (hv_HalfHeadWidth * hv_DC);
    hv_ColP1 = (hv_Column1 + ((hv_Length - hv_HeadLength) * hv_DC)) - (hv_HalfHeadWidth * hv_DR);
    hv_RowP2 = (hv_Row1 + ((hv_Length - hv_HeadLength) * hv_DR)) - (hv_HalfHeadWidth * hv_DC);
    hv_ColP2 = (hv_Column1 + ((hv_Length - hv_HeadLength) * hv_DC)) + (hv_HalfHeadWidth * hv_DR);
    //
    //Finally create output XLD contour for each input point pair
    {
        HTuple end_val45 = (hv_Length.TupleLength()) - 1;
        HTuple step_val45 = 1;
        for (hv_Index = 0; hv_Index.Continue(end_val45, step_val45); hv_Index += step_val45)
        {
            if (0 != (int(HTuple(hv_Length[hv_Index]) == -1)))
            {
                //Create_ single points for arrows with identical start and end point
                GenContourPolygonXld(&ho_TempArrow, HTuple(hv_Row1[hv_Index]), HTuple(hv_Column1[hv_Index]));
            }
            else
            {
                //Create arrow contour
                GenContourPolygonXld(&ho_TempArrow, ((((HTuple(hv_Row1[hv_Index]).TupleConcat(HTuple(hv_Row2[hv_Index]))).TupleConcat(HTuple(hv_RowP1[hv_Index]))).TupleConcat(HTuple(hv_Row2[hv_Index]))).TupleConcat(HTuple(hv_RowP2[hv_Index]))).TupleConcat(HTuple(hv_Row2[hv_Index])),
                    ((((HTuple(hv_Column1[hv_Index]).TupleConcat(HTuple(hv_Column2[hv_Index]))).TupleConcat(HTuple(hv_ColP1[hv_Index]))).TupleConcat(HTuple(hv_Column2[hv_Index]))).TupleConcat(HTuple(hv_ColP2[hv_Index]))).TupleConcat(HTuple(hv_Column2[hv_Index])));
            }
            ConcatObj((*ho_Arrow), ho_TempArrow, &(*ho_Arrow));
        }
    }
    return;
}


//
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//#region 各种应用类
//
//#region 3D预处理工具
//
//
//
//
//
//
////预处理图像函数接口
//public class CPreProcess
//{
//
//    //构造
//    public CPreProcess()
//    {
//
//    }
//
//
//    public s_Rtnf OnPreProcess(s_Image3dS sImage3dS, s_PreProcess3DSPara spara1, ref s_PreProcess3DSResultPara spara2)
//    {
//
//        s_Rtnf sError = new s_Rtnf();
//
//        sError.iCode = -1;
//        sError.strInfo = "";
//
//        spara2.bTJG = false;
//        spara2.time = 0.0;
//        spara2.sImage3dPro.Clear();
//
//
//        HTuple time_start = 0.0;
//        HTuple time_end = 0.0;
//        HOperatorSet.CountSeconds(out time_start);
//
//
//        // Local iconic variables 
//        HObject ho_X = null, ho_Y = null, ho_Z = null, ho_NX = null;
//        HObject ho_NY = null, ho_NZ = null, /*ho_Texture = null,*/ ho_GrayImage = null;
//        HObject ho_Region = null, ho_X1 = null, ho_Y1 = null, ho_Z1 = null;
//        HObject ho_Region1 = null, ho_Region2 = null, ho_Region3 = null;
//        HObject ho_NX1 = null, ho_NY1 = null, ho_NZ1 = null;
//        HObject ho_Domain = null, ho_GrayImage1 = null;
//
//        HObject ho_Image1 = null, ho_Image2 = null;
//        HObject ho_Image3 = null, ho_ImageH = null, ho_ImageS = null;
//        HObject ho_ImageV = null, ho_ImageR = null, ho_ImageG = null;
//        HObject ho_ImageB = null, ho_Multichannel = null;
//
//        // Local control variables 
//
//        HTuple hv_ImageWidth = new HTuple();
//        HTuple hv_ImageHeight = new HTuple(), hv_WindowWidth = new HTuple();
//        HTuple hv_WindowHeight = new HTuple();
//        HTuple hv_GenParamName = new HTuple(), hv_GenParamValue = new HTuple();
//
//        HTuple hv_ObjectModel3D = new HTuple(), hv_PoseOut = new HTuple();
//        HTuple hv_Rows = new HTuple(), hv_Columns = new HTuple();
//        HTuple hv_NXV = new HTuple(), hv_NYV = new HTuple(), hv_NZV = new HTuple();
//        HTuple hv_Intensity = new HTuple(), hv_Pose = new HTuple();
//        HTuple hv_ObjectModel3DConnected = new HTuple(), hv_ObjectModel3DSelected = new HTuple();
//        HTuple hv_ObjectModel3DSelected2 = new HTuple(), hv_UnionObjectModel3D = new HTuple();
//
//        HTuple hv_SampledObjectModel3DS1 = new HTuple();
//        HTuple hv_ObjectModel3DConnectedS1 = new HTuple(), hv_GPVS1 = new HTuple();
//        HTuple hv_MaxS1 = new HTuple(), hv_ObjectModel3DSelectedS1a = new HTuple();
//        HTuple hv_ObjectModel3DConnectedS1a = new HTuple(), hv_GPVS1a = new HTuple();
//        HTuple hv_MaxS1a = new HTuple(), hv_ObjectModel3DSelectedS1b = new HTuple();
//        HTuple hv_UnionObjectModel3DS1 = new HTuple(), hv_OM3DPlane = new HTuple();
//        HTuple hv_ParFitting = new HTuple(), hv_ValFitting = new HTuple();
//        HTuple hv_ObjectModel3DOutID = new HTuple(), hv_GenParamPosePlane = new HTuple();
//        HTuple hv_PlaneDatum = new HTuple(), hv_GenParamValueDistancePlane = new HTuple();
//        HTuple hv_ObjectModel3DThresholdedS1c = new HTuple(), hv_PoseOutA = new HTuple();
//        HTuple hv_UnionObjectModel3DS12 = new HTuple(), hv_ObjectModel3DConnectedS1d = new HTuple();
//        HTuple hv_ObjectModel3DSelectedS1d = new HTuple();
//
//
//        HTuple hv_RV = new HTuple(), hv_GV = new HTuple(), hv_BV = new HTuple();
//        HTuple hv_GvBoundingBox1S0 = new HTuple();
//        HTuple hv_lObjectModel3DS0 = new HTuple(), hv_ObjectModel3DSelectedS0 = new HTuple();
//
//        HTuple hv_NumPts = new HTuple();
//
//        // Initialize local and output iconic variables 
//        HOperatorSet.GenEmptyObj(out ho_X);
//        HOperatorSet.GenEmptyObj(out ho_Y);
//        HOperatorSet.GenEmptyObj(out ho_Z);
//        HOperatorSet.GenEmptyObj(out ho_NX);
//        HOperatorSet.GenEmptyObj(out ho_NY);
//        HOperatorSet.GenEmptyObj(out ho_NZ);
//        //HOperatorSet.GenEmptyObj(out ho_Texture);
//        HOperatorSet.GenEmptyObj(out ho_GrayImage);
//        HOperatorSet.GenEmptyObj(out ho_Region);
//        HOperatorSet.GenEmptyObj(out ho_Region1);
//        HOperatorSet.GenEmptyObj(out ho_Region2);
//        HOperatorSet.GenEmptyObj(out ho_Region3);
//        HOperatorSet.GenEmptyObj(out ho_X1);
//        HOperatorSet.GenEmptyObj(out ho_Y1);
//        HOperatorSet.GenEmptyObj(out ho_Z1);
//        HOperatorSet.GenEmptyObj(out ho_NX1);
//        HOperatorSet.GenEmptyObj(out ho_NY1);
//        HOperatorSet.GenEmptyObj(out ho_NZ1);
//        HOperatorSet.GenEmptyObj(out ho_Domain);
//        HOperatorSet.GenEmptyObj(out ho_GrayImage1);
//
//        HOperatorSet.GenEmptyObj(out ho_Image1);
//        HOperatorSet.GenEmptyObj(out ho_Image2);
//        HOperatorSet.GenEmptyObj(out ho_Image3);
//        HOperatorSet.GenEmptyObj(out ho_ImageH);
//        HOperatorSet.GenEmptyObj(out ho_ImageS);
//        HOperatorSet.GenEmptyObj(out ho_ImageV);
//        HOperatorSet.GenEmptyObj(out ho_ImageR);
//        HOperatorSet.GenEmptyObj(out ho_ImageG);
//        HOperatorSet.GenEmptyObj(out ho_ImageB);
//        HOperatorSet.GenEmptyObj(out ho_Multichannel);
//
//        try
//        {
//
//            s_Image3dS Image = sImage3dS;
//
//
//            //判断输入
//            if (Image.Z == null || !Image.Z.IsInitialized() || Image.Z.CountObj() == 0)
//            {
//                HOperatorSet.CountSeconds(out time_end);
//                spara2.time = time_end - time_start;
//
//                sError.iCode = 1;
//                sError.strInfo = "图像为空!";
//                return sError;
//            }
//
//
//            //处理算法
//
//
//
//
//            //ROI区域图像 并给点云附加属性
//            ho_Region.Dispose();
//            ho_Region1.Dispose();
//            ho_Region2.Dispose();
//            ho_Region3.Dispose();
//            HOperatorSet.Threshold(Image.Z, out ho_Region1, spara1.fRoiZMin, spara1.fRoiZMax);
//            HOperatorSet.Threshold(Image.X, out ho_Region2, spara1.fRoiXMin, spara1.fRoiXMax);
//            HOperatorSet.Threshold(Image.Y, out ho_Region3, spara1.fRoiYMin, spara1.fRoiYMax);
//            HOperatorSet.Intersection(ho_Region1, ho_Region2, out ho_Region);
//            HOperatorSet.Intersection(ho_Region3, ho_Region, out ho_Region);
//
//
//            ho_X.Dispose();
//            ho_Y.Dispose();
//            ho_Z.Dispose();
//            ho_NX.Dispose();
//            ho_NY.Dispose();
//            ho_NZ.Dispose();
//            ho_GrayImage.Dispose();
//
//
//
//            HOperatorSet.ReduceDomain(Image.X, ho_Region, out ho_X);
//            HOperatorSet.ReduceDomain(Image.Y, ho_Region, out ho_Y);
//            HOperatorSet.ReduceDomain(Image.Z, ho_Region, out ho_Z);
//            HOperatorSet.ReduceDomain(Image.NX, ho_Region, out ho_NX);
//            HOperatorSet.ReduceDomain(Image.NY, ho_Region, out ho_NY);
//            HOperatorSet.ReduceDomain(Image.NZ, ho_Region, out ho_NZ);
//            HOperatorSet.ReduceDomain(Image.Gray, ho_Region, out ho_GrayImage);
//
//            //灰度自动调整
//            {
//                HTuple hv_Min = new HTuple(), hv_Max = new HTuple(), hv_Range = new HTuple(), hv_Mean = new HTuple(), hv_Deviation = new HTuple();
//
//                HObject ho_ROI_0, ho_ImageTextureReduced, ho_ImageScaled;
//                HOperatorSet.GenEmptyObj(out ho_ROI_0);
//                HOperatorSet.GenEmptyObj(out ho_ImageTextureReduced);
//                HOperatorSet.GenEmptyObj(out ho_ImageScaled);
//
//
//                hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                HOperatorSet.MinMaxGray(ho_GrayImage, ho_GrayImage, 0, out hv_Min, out hv_Max,
//                    out hv_Range);
//                ho_ROI_0.Dispose();
//                HOperatorSet.GenRectangle1(out ho_ROI_0, 565.043, 729.802, 1220.68, 1362.76);
//                ho_ImageTextureReduced.Dispose();
//                HOperatorSet.ReduceDomain(ho_GrayImage, ho_ROI_0, out ho_ImageTextureReduced
//                );
//                hv_Mean.Dispose(); hv_Deviation.Dispose();
//                HOperatorSet.Intensity(ho_ROI_0, ho_ImageTextureReduced, out hv_Mean, out hv_Deviation);
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    ho_ImageScaled.Dispose();
//                    new HVisionAdv().scale_image_range(ho_GrayImage, out ho_ImageScaled, (new HTuple(0)).TupleConcat(
//                        0), ((hv_Mean * 1.2)).TupleConcat(255));
//                }
//                ho_GrayImage.Dispose();
//                HOperatorSet.CopyImage(ho_ImageScaled, out ho_GrayImage);
//
//            }
//
//
//            hv_ObjectModel3D.Dispose();
//            HOperatorSet.XyzToObjectModel3d(ho_X, ho_Y, ho_Z, out hv_ObjectModel3D);
//
//
//            hv_NumPts.Dispose();
//            HOperatorSet.GetObjectModel3dParams(hv_ObjectModel3D, "num_points", out hv_NumPts);
//
//            hv_Rows.Dispose(); hv_Columns.Dispose();
//            HOperatorSet.GetRegionPoints(ho_Region, out hv_Rows, out hv_Columns);
//
//
//
//
//            //法线属性
//            try
//            {
//
//                hv_NXV.Dispose();
//                HOperatorSet.GetGrayval(ho_NX, hv_Rows, hv_Columns, out hv_NXV);
//                hv_NYV.Dispose();
//                HOperatorSet.GetGrayval(ho_NY, hv_Rows, hv_Columns, out hv_NYV);
//                hv_NZV.Dispose();
//                HOperatorSet.GetGrayval(ho_NZ, hv_Rows, hv_Columns, out hv_NZV);
//
//                HOperatorSet.SetObjectModel3dAttribMod(hv_ObjectModel3D, ((new HTuple("point_normal_x")).TupleConcat(
//                    "point_normal_y")).TupleConcat("point_normal_z"), new HTuple(), ((hv_NXV.TupleConcat(
//                        hv_NYV))).TupleConcat(hv_NZV));
//            }
//            catch (HalconException ex)
//            {
//
//
//            }
//
//
//            //灰度属性
//            try
//            {
//
//                hv_Intensity.Dispose();
//                HOperatorSet.GetGrayval(ho_GrayImage, hv_Rows, hv_Columns, out hv_Intensity);
//                HOperatorSet.SetObjectModel3dAttribMod(hv_ObjectModel3D, "&intensity", "points", hv_Intensity);
//            }
//            catch (HalconException ex)
//            {
//
//
//            }
//
//
//
//            try
//            {
//                //法线渲染成RGB
//                ho_Image1.Dispose();
//                ho_Image2.Dispose();
//                ho_Image3.Dispose();
//                ho_ImageH.Dispose(); ho_ImageS.Dispose(); ho_ImageV.Dispose();
//                ho_ImageR.Dispose(); ho_ImageG.Dispose(); ho_ImageB.Dispose();
//                ho_Multichannel.Dispose();
//                hv_RV.Dispose(); hv_GV.Dispose(); hv_BV.Dispose();
//
//                HOperatorSet.ScaleImageMax(ho_NX, out ho_Image1);
//                HOperatorSet.ScaleImageMax(ho_NY, out ho_Image2);
//                HOperatorSet.ScaleImageMax(ho_NZ, out ho_Image3);
//                HOperatorSet.TransFromRgb(ho_Image1, ho_Image2, ho_Image3, out ho_ImageH, out ho_ImageS, out ho_ImageV, "hsv");
//                HOperatorSet.TransToRgb(ho_ImageH, ho_ImageS, ho_ImageV, out ho_ImageR, out ho_ImageG, out ho_ImageB, "hsv");
//                HOperatorSet.Compose3(ho_ImageR, ho_ImageG, ho_ImageB, out ho_Multichannel);
//
//                HOperatorSet.GetGrayval(ho_ImageR, hv_Rows, hv_Columns, out hv_RV);
//                HOperatorSet.GetGrayval(ho_ImageG, hv_Rows, hv_Columns, out hv_GV);
//                HOperatorSet.GetGrayval(ho_ImageB, hv_Rows, hv_Columns, out hv_BV);
//                HOperatorSet.SetObjectModel3dAttribMod(hv_ObjectModel3D, "&red", "points", hv_RV);
//                HOperatorSet.SetObjectModel3dAttribMod(hv_ObjectModel3D, "&green", "points", hv_GV);
//                HOperatorSet.SetObjectModel3dAttribMod(hv_ObjectModel3D, "&blue", "points", hv_BV);
//            }
//            catch (HalconException ex)
//            {
//
//
//            }
//
//
//
//
//
//            //聚类分割  根据点数 直径
//            if (true)
//            {
//                hv_ObjectModel3DConnected.Dispose();
//                HOperatorSet.ConnectionObjectModel3d(hv_ObjectModel3D, "distance_3d", spara1.fThSeg0Dis,
//                    out hv_ObjectModel3DConnected);
//                hv_ObjectModel3DSelected.Dispose();
//                HOperatorSet.SelectObjectModel3d(hv_ObjectModel3DConnected, "num_points",
//                    "and", spara1.iThSeg0NumPtsMin, spara1.iThSeg0NumPtsMax, out hv_ObjectModel3DSelected);
//                hv_ObjectModel3DSelected2.Dispose();
//                HOperatorSet.SelectObjectModel3d(hv_ObjectModel3DSelected, "diameter_bounding_box",
//                    "and", spara1.fThSeg0DiameterMin, spara1.fThSeg0DiameterMax, out hv_ObjectModel3DSelected2);
//
//                hv_UnionObjectModel3D.Dispose();
//                HOperatorSet.UnionObjectModel3d(hv_ObjectModel3DSelected2, "points_surface", out hv_UnionObjectModel3D);
//            }
//
//
//            //到背景平面距离
//            if (spara1.bUseDisToPlane)
//            {
//
//                hv_SampledObjectModel3DS1.Dispose();
//                HOperatorSet.SampleObjectModel3d(hv_ObjectModel3D, "fast_compute_normals",
//                    spara1.fSampleDtp, new HTuple(), new HTuple(), out hv_SampledObjectModel3DS1);
//                hv_PoseOut.Dispose();
//
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_ObjectModel3DConnectedS1.Dispose();
//                    HOperatorSet.ConnectionObjectModel3d(hv_SampledObjectModel3DS1, "angle",
//                        (spara1.fThSegAngleDtp * 3.14) / 180, out hv_ObjectModel3DConnectedS1);
//                }
//
//
//                hv_GPVS1.Dispose();
//                HOperatorSet.GetObjectModel3dParams(hv_ObjectModel3DConnectedS1, "num_points",
//                    out hv_GPVS1);
//                hv_MaxS1.Dispose();
//                HOperatorSet.TupleMax(hv_GPVS1, out hv_MaxS1);
//                hv_ObjectModel3DSelectedS1a.Dispose();
//                HOperatorSet.SelectObjectModel3d(hv_ObjectModel3DConnectedS1, "num_points",
//                    "and", hv_MaxS1, hv_MaxS1, out hv_ObjectModel3DSelectedS1a);
//
//                hv_ObjectModel3DConnectedS1a.Dispose();
//                HOperatorSet.ConnectionObjectModel3d(hv_ObjectModel3DSelectedS1a, "distance_3d",
//                    spara1.fThSegDisDtp, out hv_ObjectModel3DConnectedS1a);
//                hv_GPVS1a.Dispose();
//                HOperatorSet.GetObjectModel3dParams(hv_ObjectModel3DConnectedS1a, "num_points",
//                    out hv_GPVS1a);
//
//                hv_MaxS1a.Dispose();
//                HOperatorSet.TupleMax(hv_GPVS1a, out hv_MaxS1a);
//                hv_ObjectModel3DSelectedS1b.Dispose();
//                HOperatorSet.SelectObjectModel3d(hv_ObjectModel3DConnectedS1a, "num_points",
//                    "and", hv_MaxS1a, hv_MaxS1a, out hv_ObjectModel3DSelectedS1b);
//
//                hv_UnionObjectModel3DS1.Dispose();
//                HOperatorSet.UnionObjectModel3d(hv_ObjectModel3DSelectedS1b, "points_surface",
//                    out hv_UnionObjectModel3DS1);
//
//                //平面拟合
//                hv_OM3DPlane.Dispose();
//                HOperatorSet.CopyObjectModel3d(hv_UnionObjectModel3DS1, "all", out hv_OM3DPlane);
//                hv_ParFitting.Dispose();
//                hv_ParFitting = new HTuple();
//                hv_ParFitting[0] = "primitive_type";
//                hv_ParFitting[1] = "fitting_algorithm";
//                hv_ValFitting.Dispose();
//                hv_ValFitting = new HTuple();
//                hv_ValFitting[0] = "plane";
//                hv_ValFitting[1] = "least_squares_tukey";
//                hv_ObjectModel3DOutID.Dispose();
//                HOperatorSet.FitPrimitivesObjectModel3d(hv_OM3DPlane, hv_ParFitting, hv_ValFitting,
//                    out hv_ObjectModel3DOutID);
//                hv_GenParamPosePlane.Dispose();
//                HOperatorSet.GetObjectModel3dParams(hv_ObjectModel3DOutID, "primitive_pose",
//                    out hv_GenParamPosePlane);
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_PlaneDatum.Dispose();
//                    HOperatorSet.GenPlaneObjectModel3d(hv_GenParamPosePlane, (((new HTuple(-1)).TupleConcat(
//                        -1)).TupleConcat(1)).TupleConcat(1) * 900, (((new HTuple(-1)).TupleConcat(
//                            1)).TupleConcat(1)).TupleConcat(-1) * 900, out hv_PlaneDatum);
//                }
//
//
//
//                //提取到拟合平面距离范围的点云
//                HOperatorSet.DistanceObjectModel3d(hv_UnionObjectModel3D, hv_PlaneDatum,
//                    new HTuple(), 0, "signed_distances", "true");
//                hv_GenParamValueDistancePlane.Dispose();
//                HOperatorSet.GetObjectModel3dParams(hv_UnionObjectModel3D, "&distance",
//                    out hv_GenParamValueDistancePlane);
//                hv_ObjectModel3DThresholdedS1c.Dispose();
//                HOperatorSet.SelectPointsObjectModel3d(hv_UnionObjectModel3D, "&distance",
//                    spara1.fPtsSelToPlaneDisMin, spara1.fPtsSelToPlaneDisMax, out hv_ObjectModel3DThresholdedS1c);
//                ;
//
//                hv_UnionObjectModel3DS12.Dispose();
//                HOperatorSet.UnionObjectModel3d(hv_ObjectModel3DThresholdedS1c, "points_surface",
//                    out hv_UnionObjectModel3DS12);
//
//                hv_ObjectModel3DConnectedS1d.Dispose();
//                HOperatorSet.ConnectionObjectModel3d(hv_UnionObjectModel3DS12, "distance_3d",
//                    spara1.fThSeg2DisDtp, out hv_ObjectModel3DConnectedS1d);
//                hv_ObjectModel3DSelectedS1d.Dispose();
//                HOperatorSet.SelectObjectModel3d(hv_ObjectModel3DConnectedS1d, "num_points",
//                    "and", spara1.iThSeg2NumPtsMinDtp, spara1.iThSeg2NumPtsMaxDtp, out hv_ObjectModel3DSelectedS1d);
//
//
//                hv_UnionObjectModel3D.Dispose();
//                HOperatorSet.UnionObjectModel3d(hv_ObjectModel3DSelectedS1d, "points_surface", out hv_UnionObjectModel3D);
//
//            }
//
//            hv_NumPts.Dispose();
//            HOperatorSet.GetObjectModel3dParams(hv_UnionObjectModel3D, "num_points", out hv_NumPts);
//
//            //根据处理后点云区域 获得XYZ NXYZ Gray 
//            ho_X1.Dispose(); ho_Y1.Dispose(); ho_Z1.Dispose();
//            HOperatorSet.ObjectModel3dToXyz(out ho_X1, out ho_Y1, out ho_Z1, hv_UnionObjectModel3D, "from_xyz_map", new HTuple(), new HTuple());
//
//
//            ho_Domain.Dispose();
//            HOperatorSet.GetDomain(ho_Z1, out ho_Domain);
//
//            //HOperatorSet.ReduceDomain(ho_X, ho_Domain, out ho_X1);
//            //HOperatorSet.ReduceDomain(ho_Y, ho_Domain, out ho_Y1);
//            //HOperatorSet.ReduceDomain(ho_Z, ho_Domain, out ho_Z1);
//            HOperatorSet.ReduceDomain(ho_NX, ho_Domain, out ho_NX1);
//            HOperatorSet.ReduceDomain(ho_NY, ho_Domain, out ho_NY1);
//            HOperatorSet.ReduceDomain(ho_NZ, ho_Domain, out ho_NZ1);
//
//
//            ho_GrayImage1.Dispose();
//            HOperatorSet.ReduceDomain(ho_GrayImage, ho_Domain, out ho_GrayImage1);
//
//
//            //结果数据
//
//            spara2.sImage3dPro.ID = Image.ID;
//
//            if (hv_UnionObjectModel3D.Length > 0)
//            {
//                HOperatorSet.CopyObjectModel3d(hv_UnionObjectModel3D, "all", out spara2.sImage3dPro.ObjectModel3D);
//            }
//
//            spara2.sImage3dPro.Gray = ho_GrayImage1.Clone();
//            spara2.sImage3dPro.X = ho_X1.Clone();
//            spara2.sImage3dPro.Y = ho_Y1.Clone();
//            spara2.sImage3dPro.Z = ho_Z1.Clone();
//            spara2.sImage3dPro.NX = ho_NX1.Clone();
//            spara2.sImage3dPro.NY = ho_NY1.Clone();
//            spara2.sImage3dPro.NZ = ho_NZ1.Clone();
//
//
//            //释放所有临时变量
//            ho_X.Dispose();
//            ho_Y.Dispose();
//            ho_Z.Dispose();
//            ho_NX.Dispose();
//            ho_NY.Dispose();
//            ho_NZ.Dispose();
//            //ho_Texture.Dispose();
//            ho_GrayImage.Dispose();
//            ho_Region1.Dispose();
//            ho_Region2.Dispose();
//            ho_Region3.Dispose();
//            ho_Region.Dispose();
//            ho_X1.Dispose();
//            ho_Y1.Dispose();
//            ho_Z1.Dispose();
//            ho_Domain.Dispose();
//            ho_NX1.Dispose();
//            ho_NY1.Dispose();
//            ho_NZ1.Dispose();
//            ho_GrayImage1.Dispose();
//
//            hv_ImageWidth.Dispose();
//            hv_ImageHeight.Dispose();
//            hv_WindowWidth.Dispose();
//            hv_WindowHeight.Dispose();
//
//            hv_GenParamName.Dispose();
//            hv_GenParamValue.Dispose();
//
//            hv_ObjectModel3D.Dispose();
//            hv_PoseOut.Dispose();
//            hv_Rows.Dispose();
//            hv_Columns.Dispose();
//            hv_NXV.Dispose();
//            hv_NYV.Dispose();
//            hv_NZV.Dispose();
//            hv_Intensity.Dispose();
//            hv_Pose.Dispose();
//            hv_ObjectModel3DConnected.Dispose();
//            hv_ObjectModel3DSelected.Dispose();
//            hv_ObjectModel3DSelected2.Dispose();
//            hv_UnionObjectModel3D.Dispose();
//            hv_SampledObjectModel3DS1.Dispose();
//            hv_ObjectModel3DConnectedS1.Dispose();
//            hv_GPVS1.Dispose();
//            hv_MaxS1.Dispose();
//            hv_ObjectModel3DSelectedS1a.Dispose();
//            hv_ObjectModel3DConnectedS1a.Dispose();
//            hv_GPVS1a.Dispose();
//            hv_MaxS1a.Dispose();
//            hv_ObjectModel3DSelectedS1b.Dispose();
//            hv_UnionObjectModel3DS1.Dispose();
//            hv_OM3DPlane.Dispose();
//            hv_ParFitting.Dispose();
//            hv_ValFitting.Dispose();
//            hv_ObjectModel3DOutID.Dispose();
//            hv_GenParamPosePlane.Dispose();
//            hv_PlaneDatum.Dispose();
//            hv_GenParamValueDistancePlane.Dispose();
//            hv_ObjectModel3DThresholdedS1c.Dispose();
//            hv_PoseOutA.Dispose();
//            hv_UnionObjectModel3DS12.Dispose();
//            hv_ObjectModel3DConnectedS1d.Dispose();
//            hv_ObjectModel3DSelectedS1d.Dispose();
//
//            spara2.bTJG = true;
//
//            HOperatorSet.CountSeconds(out time_end);
//            spara2.time = time_end - time_start;
//
//
//            sError.iCode = 0;
//            sError.strInfo = "";
//            return sError;
//        }
//        catch (HalconException ex)
//        {
//
//
//            //释放所有临时变量
//            ho_X.Dispose();
//            ho_Y.Dispose();
//            ho_Z.Dispose();
//            ho_NX.Dispose();
//            ho_NY.Dispose();
//            ho_NZ.Dispose();
//            //ho_Texture.Dispose();
//            ho_GrayImage.Dispose();
//            ho_Region.Dispose();
//            ho_X1.Dispose();
//            ho_Y1.Dispose();
//            ho_Z1.Dispose();
//            ho_Domain.Dispose();
//            ho_NX1.Dispose();
//            ho_NY1.Dispose();
//            ho_NZ1.Dispose();
//            ho_GrayImage1.Dispose();
//
//            hv_ImageWidth.Dispose();
//            hv_ImageHeight.Dispose();
//            hv_WindowWidth.Dispose();
//            hv_WindowHeight.Dispose();
//
//            hv_GenParamName.Dispose();
//            hv_GenParamValue.Dispose();
//
//            hv_ObjectModel3D.Dispose();
//            hv_PoseOut.Dispose();
//            hv_Rows.Dispose();
//            hv_Columns.Dispose();
//            hv_NXV.Dispose();
//            hv_NYV.Dispose();
//            hv_NZV.Dispose();
//            hv_Intensity.Dispose();
//            hv_Pose.Dispose();
//            hv_ObjectModel3DConnected.Dispose();
//            hv_ObjectModel3DSelected.Dispose();
//            hv_ObjectModel3DSelected2.Dispose();
//            hv_UnionObjectModel3D.Dispose();
//
//            string str = ex.ToString();
//            CLogTxt.WriteTxt(str);
//
//            HOperatorSet.CountSeconds(out time_end);
//            spara2.time = time_end - time_start;
//
//            sError.iCode = -1;
//            sError.strInfo = "预处理失败!";
//            return sError;
//
//        }
//    }
//
//
//}
//
//
//#endregion
//
//
//#region 铜粒子打磨项目
////
////阴极板缺陷参数
//public class s_DefectPlateBPara
//{
//
//    public double fThNZAbsVal;
//    public double fThNXAbsVal;
//    public double fThNYAbsVal;
//    public double fThGrayVal;
//
//    public double fQgOffsetL;
//    public double fQgOffsetR;
//    public double fQgOffsetU;
//    public double fQgOffsetD;
//
//
//    public double fThBulgeLower;
//    public double fThBulgeHiger;
//
//    public double fQgHOrg;
//    public double fQgExCol;
//    public double fQgExRow;
//    public double fQgThOffset;
//
//    public double fConnectionDis;
//
//    public s_DefectPlateBPara()
//    {
//
//    }
//
//    public s_DefectPlateBPara DeepCopy()
//    {
//        s_DefectPlateBPara As = new s_DefectPlateBPara();
//
//        As.fThNZAbsVal = fThNZAbsVal;
//        As.fThNXAbsVal = fThNXAbsVal;
//        As.fThNYAbsVal = fThNYAbsVal;
//        As.fThGrayVal = fThGrayVal;
//
//        As.fQgOffsetL = fQgOffsetL;
//        As.fQgOffsetR = fQgOffsetR;
//        As.fQgOffsetU = fQgOffsetU;
//        As.fQgOffsetD = fQgOffsetD;
//
//
//        As.fThBulgeLower = fThBulgeLower;
//        As.fThBulgeHiger = fThBulgeHiger;
//
//        As.fQgHOrg = fQgHOrg;
//        As.fQgExCol = fQgExCol;
//        As.fQgExRow = fQgExRow;
//        As.fQgThOffset = fQgThOffset;
//
//        As.fConnectionDis = fConnectionDis;
//
//        return As;
//    }
//
//}
//
////阴极板缺陷结果参数
//public class s_DefectPlateBRtsPara
//{
//    public bool bTJG;         //综合判断
//    public double time;
//
//    public HTuple PoseTb;
//
//    public HObject X1;
//    public HObject Y1;
//    public HObject Z1;
//    public HObject ImageSubZ1;
//    public HObject ImageZ1ZeroReal;
//
//    public HObject Z1PZero;
//    public HObject X1PZero;
//    public HObject Y1PZero;
//
//    public HObject RectPartLzC;
//    public HObject RectPartLzU;
//    public HObject RectPartLzL;
//    public HObject RectPartLzD;
//    public HObject RectPartLzR;
//
//
//    public HObject RectangleQgSort;
//
//    public HTuple OM3ImageAdv;      //3D结果  
//
//
//    public s_DefectPlateBRtsPara()
//    {
//        bTJG = false;
//        time = 0.0;
//
//        //数值结果
//        PoseTb = new HTuple();
//
//        //2D结果
//        HOperatorSet.GenEmptyObj(out X1);
//        HOperatorSet.GenEmptyObj(out Y1);
//        HOperatorSet.GenEmptyObj(out Z1);
//        HOperatorSet.GenEmptyObj(out ImageSubZ1);
//        HOperatorSet.GenEmptyObj(out ImageZ1ZeroReal);
//        HOperatorSet.GenEmptyObj(out Z1PZero);
//        HOperatorSet.GenEmptyObj(out X1PZero);
//        HOperatorSet.GenEmptyObj(out Y1PZero);
//        HOperatorSet.GenEmptyObj(out RectPartLzC);
//        HOperatorSet.GenEmptyObj(out RectPartLzU);
//        HOperatorSet.GenEmptyObj(out RectPartLzL);
//        HOperatorSet.GenEmptyObj(out RectPartLzD);
//        HOperatorSet.GenEmptyObj(out RectPartLzR);
//
//
//        HOperatorSet.GenEmptyObj(out RectangleQgSort);
//
//
//        //3D结果  
//        OM3ImageAdv = new HTuple();
//
//    }
//
//    public s_DefectPlateBRtsPara DeepCopy()
//    {
//        s_DefectPlateBRtsPara As = new s_DefectPlateBRtsPara();
//
//
//        As.bTJG = bTJG;
//        As.time = time;
//
//        As.PoseTb = new HTuple(PoseTb);
//
//        //2D
//
//        As.X1.Dispose();
//        if (X1 != null && X1.IsInitialized()) { As.X1 = X1.Clone(); };
//        As.Y1.Dispose();
//        if (Y1 != null && Y1.IsInitialized()) { As.Y1 = Y1.Clone(); };
//        As.Z1.Dispose();
//        if (Z1 != null && Z1.IsInitialized()) { As.Z1 = Z1.Clone(); };
//
//
//
//
//        As.ImageSubZ1.Dispose();
//        if (ImageSubZ1 != null && ImageSubZ1.IsInitialized()) { As.ImageSubZ1 = ImageSubZ1.Clone(); };
//
//        As.ImageZ1ZeroReal.Dispose();
//        if (ImageZ1ZeroReal != null && ImageZ1ZeroReal.IsInitialized()) { As.ImageZ1ZeroReal = ImageZ1ZeroReal.Clone(); };
//        As.Z1PZero.Dispose();
//        if (Z1PZero != null && Z1PZero.IsInitialized()) { As.Z1PZero = Z1PZero.Clone(); };
//        As.X1PZero.Dispose();
//        if (X1PZero != null && X1PZero.IsInitialized()) { As.X1PZero = X1PZero.Clone(); };
//        As.Y1PZero.Dispose();
//        if (Y1PZero != null && Y1PZero.IsInitialized()) { As.Y1PZero = Y1PZero.Clone(); };
//
//
//        As.RectPartLzC.Dispose();
//        if (RectPartLzC != null && RectPartLzC.IsInitialized()) { As.RectPartLzC = RectPartLzC.Clone(); };
//        As.RectPartLzU.Dispose();
//        if (RectPartLzU != null && RectPartLzU.IsInitialized()) { As.RectPartLzU = RectPartLzU.Clone(); };
//        As.RectPartLzL.Dispose();
//        if (RectPartLzL != null && RectPartLzL.IsInitialized()) { As.RectPartLzL = RectPartLzL.Clone(); };
//        As.RectPartLzD.Dispose();
//        if (RectPartLzD != null && RectPartLzD.IsInitialized()) { As.RectPartLzD = RectPartLzD.Clone(); };
//        As.RectPartLzR.Dispose();
//        if (RectPartLzR != null && RectPartLzR.IsInitialized()) { As.RectPartLzR = RectPartLzR.Clone(); };
//        As.RectangleQgSort.Dispose();
//        if (RectangleQgSort != null && RectangleQgSort.IsInitialized()) { As.RectangleQgSort = RectangleQgSort.Clone(); };
//
//
//
//        // 3D
//        As.OM3ImageAdv = new HTuple();
//        if (OM3ImageAdv.Length > 0)
//        {
//            try { HOperatorSet.CopyObjectModel3d(OM3ImageAdv, "all", out As.OM3ImageAdv); }
//            catch (HalconException ex) { ; }
//
//        }
//
//        return As;
//    }
//
//    public void Reset()
//    {
//        bTJG = false;
//        time = 0.0;
//
//        PoseTb.Dispose();
//        PoseTb = new HTuple();
//
//
//        //2D
//        X1.Dispose();
//        Y1.Dispose();
//        Z1.Dispose();
//        ImageSubZ1.Dispose();
//        ImageZ1ZeroReal.Dispose();
//
//
//        Z1PZero.Dispose();
//        X1PZero.Dispose();
//        Y1PZero.Dispose();
//
//        RectPartLzC.Dispose();
//        RectPartLzU.Dispose();
//        RectPartLzL.Dispose();
//        RectPartLzD.Dispose();
//        RectPartLzR.Dispose();
//        RectangleQgSort.Dispose();
//
//        HOperatorSet.GenEmptyObj(out X1);
//        HOperatorSet.GenEmptyObj(out Y1);
//        HOperatorSet.GenEmptyObj(out Z1);
//        HOperatorSet.GenEmptyObj(out ImageSubZ1);
//        HOperatorSet.GenEmptyObj(out ImageZ1ZeroReal);
//        HOperatorSet.GenEmptyObj(out Z1PZero);
//        HOperatorSet.GenEmptyObj(out X1PZero);
//        HOperatorSet.GenEmptyObj(out Y1PZero);
//        HOperatorSet.GenEmptyObj(out RectPartLzC);
//        HOperatorSet.GenEmptyObj(out RectPartLzU);
//        HOperatorSet.GenEmptyObj(out RectPartLzL);
//        HOperatorSet.GenEmptyObj(out RectPartLzD);
//        HOperatorSet.GenEmptyObj(out RectPartLzR);
//
//
//        HOperatorSet.GenEmptyObj(out RectangleQgSort);
//
//        //3D
//        if (OM3ImageAdv.Length > 0)
//        {
//            HOperatorSet.ClearObjectModel3d(OM3ImageAdv);
//            OM3ImageAdv.Dispose();
//        }
//
//
//    }
//
//}
//
//
////加工工艺参数
//public class s_JggyPara
//{
//
//    public double fDjDiamiter;  //刀具直径
//    public double fJgLzUpOffset;  //粒子最高点上抬距离 作为最高点
//    public double fJgDpUpOffset; //铜板上平面上抬距离作为最低点
//    public int iModeJgPPZStepMode;//规划Z路径进给模式  0 :等距进给 1：线性进给
//    public double fJgPPZStepFix;
//    public double fJgPPZStepK;
//    public double fJgPPZStepB;
//    public int iModeJgPPYStepMode; //规划Y路径进给模式  0 :固定进给 2：根据刀盘大小进给
//    public double fJgPPYStepFix;
//    public double fJgPPYStepK;
//    public int iModeJgPPSort; //粒子加工排序 0：从上到下  1 ：从左到右
//    public double fQgSafeDis;  //气缸安全距离  注意此处考虑的是加工中心点到气缸的安全距离，未考虑刀盘直径影响
//    public double fJgTdZUp;     //抬刀高度 用于起始点 或者终点 加工完后的上抬高度
//
//    public s_JggyPara DeepCopy()
//    {
//        s_JggyPara As = new s_JggyPara();
//
//
//        As.fDjDiamiter = fDjDiamiter;
//        As.fJgLzUpOffset = fJgLzUpOffset;
//        As.fJgDpUpOffset = fJgDpUpOffset;
//        As.iModeJgPPZStepMode = iModeJgPPZStepMode;
//        As.fJgPPZStepFix = fJgPPZStepFix;
//        As.fJgPPZStepK = fJgPPZStepK;
//        As.fJgPPZStepB = fJgPPZStepB;
//        As.iModeJgPPYStepMode = iModeJgPPYStepMode;
//        As.fJgPPYStepFix = fJgPPYStepFix;
//        As.fJgPPYStepK = fJgPPYStepK;
//        As.iModeJgPPSort = iModeJgPPSort;
//        As.fQgSafeDis = iModeJgPPSort;
//        As.fJgTdZUp = fJgTdZUp;
//
//        return As;
//    }
//
//
//
//}
//
////路径点位结构体
//public class s_PPts
//{
//
//    public double fX;
//    public double fY;
//    public double fZ;
//    public int iDef; //点属性定义  1 起点  2 终点  3 中间点  4空跑点
//    public double fRow;  //图像行坐标
//    public double fCol;  //图像列坐标
//    public string strQgNotSafe; //避让气缸索引  eg "0,2,4" 代表第1,3,5个气缸需要松开
//
//    public s_PPts()
//    {
//        fX = 0;
//        fY = 0;
//        fZ = 0;
//        iDef = 0;
//        fRow = 0;
//        fCol = 0;
//        strQgNotSafe = "";
//    }
//
//    public s_PPts DeepCopy()
//    {
//        s_PPts As = new s_PPts();
//        As.fX = fX;
//        As.fY = fY;
//        As.fZ = fZ;
//        As.iDef = iDef;
//        As.fRow = fRow;
//        As.fCol = fCol;
//        As.strQgNotSafe = strQgNotSafe;
//        return As;
//    }
//
//    public void Reset()
//    {
//        fX = 0;
//        fY = 0;
//        fZ = 0;
//        iDef = 0;
//        fRow = 0;
//        fCol = 0;
//        strQgNotSafe = "";
//    }
//
//}
//
////粒子路径规划结果参数结果参数
//public class s_LzppRtsPara
//{
//    public bool bTJG;         //综合判断
//    public double time;
//    public int iNumPts;
//    public List<s_PPts> sListPPts;
//    public HObject RegionMxAllList;
//
//    public s_LzppRtsPara()
//    {
//        bTJG = false;
//        time = 0.0;
//
//        iNumPts = 0;
//        sListPPts = new List<s_PPts>() { };
//        HOperatorSet.GenEmptyObj(out RegionMxAllList);
//    }
//
//    public s_LzppRtsPara DeepCopy()
//    {
//        s_LzppRtsPara As = new s_LzppRtsPara();
//
//
//        As.bTJG = bTJG;
//        As.time = time;
//
//        As.iNumPts = iNumPts;
//        As.sListPPts.Clear();
//        for (int i = 0; i < sListPPts.Count; i++)
//        {
//            As.sListPPts.Add(sListPPts[i].DeepCopy());
//        }
//        As.RegionMxAllList.Dispose();
//        if (RegionMxAllList != null && RegionMxAllList.IsInitialized()) { As.RegionMxAllList = RegionMxAllList.Clone(); };
//
//        return As;
//    }
//
//    public void Reset()
//    {
//        bTJG = false;
//        time = 0.0;
//
//        iNumPts = 0;
//        sListPPts.Clear();
//
//        RegionMxAllList.Dispose();
//        HOperatorSet.GenEmptyObj(out RegionMxAllList);
//
//    }
//
//}
//
//
////阴极板接口
//public class CPlateB
//{
//
//    //构造
//    public CPlateB()
//    {
//
//    }
//
//    ////缺陷检测+自动分区
//    public s_Rtnf OnDetect(s_Image3dS Image3d, s_DefectPlateBPara spara1, ref s_DefectPlateBRtsPara spara2)
//    {
//
//        HTuple time_start = 0.0;
//        HTuple time_end = 0.0;
//        HOperatorSet.CountSeconds(out time_start);
//
//        s_Rtnf sError = new s_Rtnf();
//        sError.iCode = -1;
//        sError.strInfo = "";
//
//
//        //复位结果数据
//        spara2.Reset();
//
//        #region 临时变量
//
//            // Stack for temporary objects 
//            HObject[] OTemp = new HObject[20];
//
//        // Local iconic variables 
//
//        HObject ho_Region = null, ho_PointCloud = null;
//        HObject ho_Normals = null, ho_X = null, ho_Y = null, ho_Gray = null;
//        HObject ho_Z = null, ho_NX = null, ho_NY = null, ho_NZ = null, ho_MultiChannelImage = null;
//        HObject ho_Region1 = null, ho_Region2 = null, ho_RegionNZ = null;
//        HObject ho_Region3 = null, ho_Region4 = null, ho_RegionNXY = null;
//        HObject ho_RegionRegionNXYZ = null, ho_RegionIntersection = null;
//        HObject ho_ImageReduced = null, ho_Xs = null, ho_Ys = null, ho_Zs = null;
//        HObject ho_Domain = null, ho_RegionFillUp = null, ho_RegionClosing = null;
//        HObject ho_RegionOpening = null, ho_RegionErosion = null, ho_RegionTb = null;
//        HObject ho_X1 = null, ho_Y1 = null, ho_Z1 = null, ho_ROI = null;
//        HObject ho_ImageSurface = null, ho_ImageSub = null, ho_ConnectedRegions = null;
//        HObject ho_SelectedRegions = null, ho_RectangleQg = null, ho_RectangleL = null;
//        HObject ho_RectangleR = null, ho_RectangleU = null, ho_RectangleD = null;
//        HObject ho_RegionDifference = null, ho_RectangleQgL = null;
//        HObject ho_RectangleQgR = null, ho_RectangleQgU = null, ho_RectangleQgD = null;
//        HObject ho_RectangleLAdv = null, ho_RectangleRAdv = null, ho_RectangleUAdv = null;
//        HObject ho_RectangleDAdv = null, ho_RectangleCAdv = null, ho_RectanglePartList = null;
//        HObject ho_RectangleQgSort = null, ho_SortedRegions = null;
//        HObject ho_ImageSubZ1 = null, ho_X1PZeroC = null, ho_Y1PZeroC = null;
//        HObject ho_Z1PZeroC = null, ho_RegionRoiCBulge = null, ho_ImageSubC = null;
//        HObject ho_Z1PZero = null, ho_X1PZero = null, ho_Y1PZero = null;
//        HObject ho_RegionRoiCBulgeUnion = null, ho_RectangleQgEx = null;
//        HObject ho_RectangleLAdvRemoveQg = null, ho_X1PZeroL = null;
//        HObject ho_Y1PZeroL = null, ho_Z1PZeroL = null, ho_Z1PZeroLRemoveQg = null;
//        HObject ho_RegionQgExL = null, ho_RegionRoiLBulgeRemoveQg = null;
//        HObject ho_ImageSubLRemoveQg = null, ho_RegionUnion = null;
//        HObject ho_RegionRoiLBulgeQg = null, ho_ImageSubLQg = null;
//        HObject ho_RectangleRAdvRemoveQg = null, ho_X1PZeroR = null;
//        HObject ho_Y1PZeroR = null, ho_Z1PZeroR = null, ho_Z1PZeroRRemoveQg = null;
//        HObject ho_RegionQgExR = null, ho_RegionRoiRBulgeRemoveQg = null;
//        HObject ho_ImageSubRRemoveQg = null, ho_RegionRoiRBulgeQg = null;
//        HObject ho_ImageSubRQg = null, ho_RectangleUAdvRemoveQg = null;
//        HObject ho_X1PZeroU = null, ho_Y1PZeroU = null, ho_Z1PZeroU = null;
//        HObject ho_Z1PZeroURemoveQg = null, ho_RegionQgExU = null, ho_RegionRoiUBulgeRemoveQg = null;
//        HObject ho_ImageSubURemoveQg = null, ho_RegionRoiUBulgeQg = null;
//        HObject ho_ImageSubUQg = null, ho_RectangleDAdvRemoveQg = null;
//        HObject ho_X1PZeroD = null, ho_Y1PZeroD = null, ho_Z1PZeroD = null;
//        HObject ho_Z1PZeroDRemoveQg = null, ho_RegionQgExD = null, ho_RegionRoiDBulgeRemoveQg = null;
//        HObject ho_ImageSubDRemoveQg = null, ho_RegionRoiDBulgeQg = null;
//        HObject ho_ImageSubDQg = null, ho_RegionRoiLBulge = null, ho_RegionRoiRBulge = null;
//        HObject ho_RegionRoiUBulge = null, ho_RegionRoiDBulge = null;
//        HObject ho_RegionPartLzC = null, ho_RectPartLzC = null, ho_RegionPartLzL = null;
//        HObject ho_RectPartLzL = null, ho_RegionPartLzR = null, ho_RectPartLzR = null;
//        HObject ho_RegionPartUzL = null, ho_RectPartLzU = null, ho_RegionPartLzD = null;
//        HObject ho_RectPartLzD = null;
//        HObject hImageRed, hImageGreen, hImageBlue;
//
//
//        HObject ho_ImageZ1ZeroReal = null, ho_ZZeroRealC = null, ho_ZZeroRealL = null, ho_ZZeroRealR = null, ho_ZZeroRealU = null, ho_ZZeroRealD = null;
//        HObject ho_ZZeroRealLQg = null, ho_ZZeroRealRQg = null, ho_ZZeroRealUQg = null, ho_ZZeroRealDQg = null;
//        HObject ho_RegionMoved = null;
//
//        HObject ho_ROI_0 = null, ho_ROI_1 = null, ho_ROI_2 = null, ho_ROI_3 = null;
//        HObject ho_ROI_4 = null, ho_ROI_5 = null, ho_ROI_6 = null, ho_ROI_7 = null;
//        HObject ho_ROI_8 = null, ho_ROI_9 = null, ho_ROI_10 = null, ho_ROI_11 = null;
//        HObject ho_ROI_12 = null, ho_ROI_13 = null, ho_ROI_14 = null, ho_ROI_15 = null;
//        HObject ho_RegionQgIn = null;
//
//
//        HObject ho_RegionQgReal = null, ho_ObjectSelected1 = null, ho_ObjectSelected2 = null, ho_EmptyRegion = null;
//
//        // Local control variables 
//
//        HTuple hv_Rows = new HTuple(), hv_Columns = new HTuple();
//        HTuple hv_Max = new HTuple(), hv_ObjectModel3DConnected = new HTuple();
//        HTuple hv_ObjectModel3DSelected = new HTuple(), hv_UnionObjectModel3D = new HTuple();
//        HTuple hv_Om3DScene = new HTuple(), hv_fThNZAbsVal = new HTuple();
//        HTuple hv_fThNXAbsVal = new HTuple(), hv_fThNYAbsVal = new HTuple();
//        HTuple hv_fThGrayVal = new HTuple(), hv_ObjectModel3D1 = new HTuple();
//        HTuple hv_GenParamValue = new HTuple(), hv_ObjectModel3DAdv = new HTuple();
//        HTuple hv_Alpha = new HTuple(), hv_Beta = new HTuple();
//        HTuple hv_Gamma = new HTuple(), hv_Area = new HTuple();
//        HTuple hv_Row = new HTuple(), hv_Column = new HTuple();
//        HTuple hv_Width = new HTuple(), hv_Height = new HTuple();
//        HTuple hv_Row1 = new HTuple(), hv_Column1 = new HTuple();
//        HTuple hv_Row2 = new HTuple(), hv_Column2 = new HTuple();
//        HTuple hv_Diameter = new HTuple(), hv_Rectangularity = new HTuple();
//        HTuple hv_fQgOffsetL = new HTuple(), hv_fQgOffsetR = new HTuple();
//        HTuple hv_fQgOffsetU = new HTuple(), hv_fQgOffsetD = new HTuple();
//        HTuple hv_ColumnL = new HTuple(), hv_ColumnR = new HTuple();
//        HTuple hv_RowU = new HTuple(), hv_RowD = new HTuple();
//        HTuple hv_Om3DC = new HTuple(), hv_SampledObjectModel3D = new HTuple();
//        HTuple hv_OM3DPlane = new HTuple(), hv_ParFitting = new HTuple();
//        HTuple hv_ValFitting = new HTuple(), hv_ObjectModel3DOutID = new HTuple();
//        HTuple hv_GenParamPosePlane = new HTuple(), hv_PlaneDatum = new HTuple();
//        HTuple hv_PoseTbC = new HTuple(), hv_PoseInvert = new HTuple();
//        HTuple hv_HomMat3D = new HTuple(), hv_OM3dPZeroC = new HTuple();
//        HTuple hv_fThBulgeLower = new HTuple(), hv_fThBulgeHiger = new HTuple();
//        HTuple hv_Grayval = new HTuple(), hv_fQgHOrg = new HTuple();
//        HTuple hv_fQgExCol = new HTuple(), hv_fQgExRow = new HTuple();
//        HTuple hv_fQgThOffset = new HTuple(), hv_Om3DL = new HTuple();
//        HTuple hv_Om3DLRemoveQg = new HTuple();
//        HTuple hv_OM3dPZeroL = new HTuple(), hv_Om3DR = new HTuple();
//        HTuple hv_Om3DRRemoveQg = new HTuple();
//        HTuple hv_OM3dPZeroR = new HTuple(), hv_Om3DU = new HTuple();
//        HTuple hv_Om3DURemoveQg = new HTuple();
//        HTuple hv_OM3dPZeroU = new HTuple(), hv_Om3DD = new HTuple();
//        HTuple hv_Om3DDRemoveQg = new HTuple();
//        HTuple hv_OM3dPZeroD = new HTuple(), hv_fConnectionDis = new HTuple();
//
//        HTuple hv_OM3dPZero = new HTuple();
//
//
//        HTuple hChannels = new HTuple();
//
//        HTuple hv_bFind = new HTuple();
//        HTuple hv_Number1 = new HTuple();
//        HTuple hv_Number2 = new HTuple();
//        HTuple hv_i = new HTuple();
//        HTuple hv_j = new HTuple();
//
//        // Initialize local and output iconic variables 
//        HOperatorSet.GenEmptyObj(out ho_Region);
//        HOperatorSet.GenEmptyObj(out ho_PointCloud);
//        HOperatorSet.GenEmptyObj(out ho_Normals);
//        HOperatorSet.GenEmptyObj(out ho_X);
//        HOperatorSet.GenEmptyObj(out ho_Y);
//        HOperatorSet.GenEmptyObj(out ho_Z);
//        HOperatorSet.GenEmptyObj(out ho_Gray);
//        HOperatorSet.GenEmptyObj(out ho_NX);
//        HOperatorSet.GenEmptyObj(out ho_NY);
//        HOperatorSet.GenEmptyObj(out ho_NZ);
//        HOperatorSet.GenEmptyObj(out ho_MultiChannelImage);
//        HOperatorSet.GenEmptyObj(out ho_Region1);
//        HOperatorSet.GenEmptyObj(out ho_Region2);
//        HOperatorSet.GenEmptyObj(out ho_RegionNZ);
//        HOperatorSet.GenEmptyObj(out ho_Region3);
//        HOperatorSet.GenEmptyObj(out ho_Region4);
//        HOperatorSet.GenEmptyObj(out ho_RegionNXY);
//        HOperatorSet.GenEmptyObj(out ho_RegionRegionNXYZ);
//        HOperatorSet.GenEmptyObj(out ho_RegionIntersection);
//        HOperatorSet.GenEmptyObj(out ho_ImageReduced);
//        HOperatorSet.GenEmptyObj(out ho_Xs);
//        HOperatorSet.GenEmptyObj(out ho_Ys);
//        HOperatorSet.GenEmptyObj(out ho_Zs);
//        HOperatorSet.GenEmptyObj(out ho_Domain);
//        HOperatorSet.GenEmptyObj(out ho_RegionFillUp);
//        HOperatorSet.GenEmptyObj(out ho_RegionClosing);
//        HOperatorSet.GenEmptyObj(out ho_RegionOpening);
//        HOperatorSet.GenEmptyObj(out ho_RegionErosion);
//        HOperatorSet.GenEmptyObj(out ho_RegionTb);
//        HOperatorSet.GenEmptyObj(out ho_X1);
//        HOperatorSet.GenEmptyObj(out ho_Y1);
//        HOperatorSet.GenEmptyObj(out ho_Z1);
//
//        HOperatorSet.GenEmptyObj(out ho_ROI);
//        HOperatorSet.GenEmptyObj(out ho_ImageSurface);
//        HOperatorSet.GenEmptyObj(out ho_ImageSub);
//        HOperatorSet.GenEmptyObj(out ho_ConnectedRegions);
//        HOperatorSet.GenEmptyObj(out ho_SelectedRegions);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQg);
//        HOperatorSet.GenEmptyObj(out ho_RectangleL);
//        HOperatorSet.GenEmptyObj(out ho_RectangleR);
//        HOperatorSet.GenEmptyObj(out ho_RectangleU);
//        HOperatorSet.GenEmptyObj(out ho_RectangleD);
//        HOperatorSet.GenEmptyObj(out ho_RegionDifference);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgL);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgR);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgU);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgD);
//        HOperatorSet.GenEmptyObj(out ho_RectangleLAdv);
//        HOperatorSet.GenEmptyObj(out ho_RectangleRAdv);
//        HOperatorSet.GenEmptyObj(out ho_RectangleUAdv);
//        HOperatorSet.GenEmptyObj(out ho_RectangleDAdv);
//        HOperatorSet.GenEmptyObj(out ho_RectangleCAdv);
//        HOperatorSet.GenEmptyObj(out ho_RectanglePartList);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgSort);
//        HOperatorSet.GenEmptyObj(out ho_SortedRegions);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubZ1);
//        HOperatorSet.GenEmptyObj(out ho_X1PZeroC);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZeroC);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroC);
//        HOperatorSet.GenEmptyObj(out ho_X1PZero);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZero);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZero);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiCBulge);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubC);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiCBulgeUnion);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgEx);
//        HOperatorSet.GenEmptyObj(out ho_RectangleLAdvRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_X1PZeroL);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZeroL);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroL);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroLRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionQgExL);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiLBulgeRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubLRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionUnion);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiLBulgeQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubLQg);
//        HOperatorSet.GenEmptyObj(out ho_RectangleRAdvRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_X1PZeroR);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZeroR);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroR);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroRRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionQgExR);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiRBulgeRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubRRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiRBulgeQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubRQg);
//        HOperatorSet.GenEmptyObj(out ho_RectangleUAdvRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_X1PZeroU);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZeroU);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroU);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroURemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionQgExU);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiUBulgeRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubURemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiUBulgeQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubUQg);
//        HOperatorSet.GenEmptyObj(out ho_RectangleDAdvRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_X1PZeroD);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZeroD);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroD);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroDRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionQgExD);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiDBulgeRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubDRemoveQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiDBulgeQg);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubDQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiLBulge);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiRBulge);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiUBulge);
//        HOperatorSet.GenEmptyObj(out ho_RegionRoiDBulge);
//        HOperatorSet.GenEmptyObj(out ho_RegionPartLzC);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzC);
//        HOperatorSet.GenEmptyObj(out ho_RegionPartLzL);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzL);
//        HOperatorSet.GenEmptyObj(out ho_RegionPartLzR);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzR);
//        HOperatorSet.GenEmptyObj(out ho_RegionPartUzL);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzU);
//        HOperatorSet.GenEmptyObj(out ho_RegionPartLzD);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzD); ;
//
//
//        HOperatorSet.GenEmptyObj(out hImageRed);
//        HOperatorSet.GenEmptyObj(out hImageGreen);
//        HOperatorSet.GenEmptyObj(out hImageBlue); ;
//
//
//        HOperatorSet.GenEmptyObj(out ho_ImageZ1ZeroReal);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealC);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealL);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealR);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealU);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealD);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealLQg);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealRQg);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealUQg);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroRealDQg);
//        HOperatorSet.GenEmptyObj(out ho_RegionMoved);
//
//        HOperatorSet.GenEmptyObj(out ho_ROI_0);
//        HOperatorSet.GenEmptyObj(out ho_ROI_1);
//        HOperatorSet.GenEmptyObj(out ho_ROI_2);
//        HOperatorSet.GenEmptyObj(out ho_ROI_3);
//        HOperatorSet.GenEmptyObj(out ho_ROI_4);
//        HOperatorSet.GenEmptyObj(out ho_ROI_5);
//        HOperatorSet.GenEmptyObj(out ho_ROI_6);
//        HOperatorSet.GenEmptyObj(out ho_ROI_7);
//        HOperatorSet.GenEmptyObj(out ho_ROI_8);
//        HOperatorSet.GenEmptyObj(out ho_ROI_9);
//        HOperatorSet.GenEmptyObj(out ho_ROI_10);
//        HOperatorSet.GenEmptyObj(out ho_ROI_11);
//        HOperatorSet.GenEmptyObj(out ho_ROI_12);
//        HOperatorSet.GenEmptyObj(out ho_ROI_13);
//        HOperatorSet.GenEmptyObj(out ho_ROI_14);
//        HOperatorSet.GenEmptyObj(out ho_ROI_15);
//        HOperatorSet.GenEmptyObj(out ho_RegionQgIn);
//
//
//        HOperatorSet.GenEmptyObj(out ho_RegionQgReal);
//        HOperatorSet.GenEmptyObj(out ho_ObjectSelected1);
//        HOperatorSet.GenEmptyObj(out ho_ObjectSelected2);
//        HOperatorSet.GenEmptyObj(out ho_EmptyRegion);
//
//
//
//
//        #endregion
//
//            while (true)
//            {
//                try
//                {
//                    ho_X.Dispose();
//                    ho_Y.Dispose();
//                    ho_Z.Dispose();
//                    ho_Gray.Dispose();
//
//                    ho_NX.Dispose();
//                    ho_NY.Dispose();
//                    ho_NZ.Dispose();
//
//
//                    ho_X = Image3d.X.Clone();
//                    ho_Y = Image3d.Y.Clone();
//                    ho_Z = Image3d.Z.Clone();
//                    ho_Gray = Image3d.Gray.Clone();
//
//                    ho_NX = Image3d.NX.Clone();
//                    ho_NY = Image3d.NY.Clone();
//                    ho_NZ = Image3d.NZ.Clone();
//
//
//                    //new HVisionAdv().WriteImage3DX(Image3d,@"D:\\lins","1");
//
//                    //判断输入
//                    if (!ho_Z.IsInitialized() || ho_Z.CountObj() == 0 || !ho_X.IsInitialized() || ho_X.CountObj() == 0 || !ho_Y.IsInitialized() || ho_Y.CountObj() == 0)
//                    {
//                        HOperatorSet.CountSeconds(out time_end);
//                        spara2.time = time_end - time_start;
//
//                        sError.iCode = 1;
//                        sError.strInfo = "图像为空!";
//                        break;
//                    }
//
//
//                    if (!ho_NZ.IsInitialized() || ho_NZ.CountObj() == 0 || !ho_NX.IsInitialized() || ho_NX.CountObj() == 0 || !ho_NY.IsInitialized() || ho_NY.CountObj() == 0)
//                    {
//                        HOperatorSet.CountSeconds(out time_end);
//                        spara2.time = time_end - time_start;
//
//                        sError.iCode = 1;
//                        sError.strInfo = "图像为空!";
//                        break;
//                    }
//
//
//                    if (!ho_Gray.IsInitialized() || ho_Gray.CountObj() == 0)
//                    {
//                        HOperatorSet.CountSeconds(out time_end);
//                        spara2.time = time_end - time_start;
//
//                        sError.iCode = 1;
//                        sError.strInfo = "图像为空!";
//                        break;
//                    }
//
//
//                    //3通道图像转成单通道
//                    HOperatorSet.CountChannels(ho_Gray, out hChannels);
//                    if (hChannels[0].I == 3)
//                    {
//                        HOperatorSet.Decompose3(ho_Gray, out hImageRed, out hImageGreen, out hImageBlue);
//                        ho_Gray.Dispose();
//                        ho_Gray = hImageRed.Clone();
//                    }
//
//
//
//
//                    #region 算法整体部分
//
//
//                        ho_ROI_0.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_0, 428, 753, 591, 831);
//                    ho_ROI_1.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_1, 433, 916, 618, 1001);
//                    ho_ROI_2.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_2, 433, 1084, 628, 1171);
//                    ho_ROI_3.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_3, 421, 1264, 611, 1331);
//
//
//                    ho_ROI_4.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_4, 671.403, 1277.93, 746.476, 1460.56);
//                    ho_ROI_5.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_5, 804.032, 1290.44, 879.105, 1473.07);
//                    ho_ROI_6.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_6, 969.192, 1277.93, 1044.26, 1460.56);
//                    ho_ROI_7.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_7, 1101.82, 1285.43, 1176.89, 1468.07);
//
//
//                    ho_ROI_8.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_8, 1189.41, 1204.13, 1299.51, 1249.16);
//                    ho_ROI_9.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_9, 1174.39, 1096.55, 1284.5, 1141.58);
//                    ho_ROI_10.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_10, 1169.96, 941.503, 1280.07, 999.045);
//                    ho_ROI_11.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_11, 1168.19, 801.624, 1278.3, 859.166);
//
//                    ho_ROI_12.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_12, 1095.66, 630.369, 1145.2, 786.024);
//                    ho_ROI_13.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_13, 976.981, 637.452, 1037.13, 793.106);
//                    ho_ROI_14.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_14, 813.996, 645.419, 874.147, 801.074);
//                    ho_ROI_15.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI_15, 631.69, 627.725, 691.841, 783.38);
//
//
//                    ho_RegionQgIn.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionQgIn);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_0, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_1, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_2, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_3, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_4, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_5, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_6, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_7, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_8, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_9, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_10, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_11, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_12, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_13, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_14, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgIn, ho_ROI_15, out ExpTmpOutVar_0);
//                        ho_RegionQgIn.Dispose();
//                        ho_RegionQgIn = ExpTmpOutVar_0;
//                    }
//
//
//
//                    //step1 各种ROI区域/点云
//
//                    //铜板整体区域
//                    hv_Om3DScene.Dispose();
//                    HOperatorSet.XyzToObjectModel3d(ho_X, ho_Y, ho_Z, out hv_Om3DScene);
//
//                    //提取铜板整体参数
//                    hv_fThNZAbsVal.Dispose();
//                    hv_fThNZAbsVal = /*0.8*/spara1.fThNZAbsVal;
//                    hv_fThNXAbsVal.Dispose();
//                    hv_fThNXAbsVal = /*0.2*/spara1.fThNXAbsVal;
//                    hv_fThNYAbsVal.Dispose();
//                    hv_fThNYAbsVal = /*0.2*/spara1.fThNYAbsVal;
//                    hv_fThGrayVal.Dispose();
//                    hv_fThGrayVal = /*50*/spara1.fThGrayVal;
//
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_Region1.Dispose();
//                        HOperatorSet.Threshold(ho_NZ, out ho_Region1, -1, -hv_fThNZAbsVal);
//                    }
//                    ho_Region2.Dispose();
//                    HOperatorSet.Threshold(ho_NZ, out ho_Region2, hv_fThNZAbsVal, 1);
//                    ho_RegionNZ.Dispose();
//                    HOperatorSet.Union2(ho_Region1, ho_Region2, out ho_RegionNZ);
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_Region3.Dispose();
//                        HOperatorSet.Threshold(ho_NX, out ho_Region3, -hv_fThNXAbsVal, hv_fThNXAbsVal);
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_Region4.Dispose();
//                        HOperatorSet.Threshold(ho_NY, out ho_Region4, -hv_fThNYAbsVal, hv_fThNYAbsVal);
//                    }
//                    ho_RegionNXY.Dispose();
//                    HOperatorSet.Intersection(ho_Region4, ho_Region3, out ho_RegionNXY);
//                    ho_RegionRegionNXYZ.Dispose();
//                    HOperatorSet.Intersection(ho_RegionNZ, ho_RegionNXY, out ho_RegionRegionNXYZ);
//
//
//                    ho_RegionIntersection.Dispose();
//                    HOperatorSet.Intersection(ho_RegionRegionNXYZ, ho_Z, out ho_RegionIntersection);
//
//
//
//
//                    ho_Region.Dispose();
//                    HOperatorSet.Threshold(ho_Gray, out ho_Region, hv_fThGrayVal, 255);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.Intersection(ho_Region, ho_RegionIntersection, out ExpTmpOutVar_0);
//                        ho_RegionIntersection.Dispose();
//                        ho_RegionIntersection = ExpTmpOutVar_0;
//                    }
//
//
//                    ho_ImageReduced.Dispose();
//                    HOperatorSet.ReduceDomain(ho_Z, ho_RegionIntersection, out ho_ImageReduced);
//
//
//
//                    hv_ObjectModel3D1.Dispose();
//                    HOperatorSet.XyzToObjectModel3d(ho_X, ho_Y, ho_ImageReduced, out hv_ObjectModel3D1);
//
//
//                    //HOperatorSet.WriteImage(ho_X, "tiff", 0, @"D:\\lins\\" + @"ho_X");
//                    //HOperatorSet.WriteImage(ho_Y, "tiff", 0, @"D:\\lins\\" + @"ho_Y");
//                    //HOperatorSet.WriteImage(ho_ImageReduced, "tiff", 0, @"D:\\lins\\" + @"ho_ImageReduced");
//                    //  new HVisionAdv().WriteRegionX(ho_RegionIntersection, @"D:\\lins\\", @"ho_RegionIntersection", true);
//
//                    hv_ObjectModel3DConnected.Dispose();
//                    HOperatorSet.ConnectionObjectModel3d(hv_ObjectModel3D1, "distance_3d", 5,
//                        out hv_ObjectModel3DConnected);
//                    hv_GenParamValue.Dispose();
//                    HOperatorSet.GetObjectModel3dParams(hv_ObjectModel3DConnected, "num_points",
//                        out hv_GenParamValue);
//                    hv_Max.Dispose();
//                    HOperatorSet.TupleMax(hv_GenParamValue, out hv_Max);
//                    hv_ObjectModel3DSelected.Dispose();
//                    HOperatorSet.SelectObjectModel3d(hv_ObjectModel3DConnected, "num_points",
//                        "and", hv_Max, hv_Max, out hv_ObjectModel3DSelected);
//
//                    ho_Xs.Dispose(); ho_Ys.Dispose(); ho_Zs.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_Xs, out ho_Ys, out ho_Zs, hv_ObjectModel3DSelected,
//                        "from_xyz_map", new HTuple(), new HTuple());
//                    ho_Domain.Dispose();
//                    HOperatorSet.GetDomain(ho_Xs, out ho_Domain);
//                    ho_RegionFillUp.Dispose();
//                    HOperatorSet.FillUp(ho_Domain, out ho_RegionFillUp);
//                    ho_RegionClosing.Dispose();
//                    HOperatorSet.ClosingRectangle1(ho_RegionFillUp, out ho_RegionClosing, 101, 101);
//                    ho_RegionOpening.Dispose();
//                    HOperatorSet.OpeningRectangle1(ho_RegionClosing, out ho_RegionOpening, 151, 151);
//
//                    ho_RegionErosion.Dispose();
//                    HOperatorSet.ErosionRectangle1(ho_RegionOpening, out ho_RegionErosion, 7, 7);
//                    ho_RegionTb.Dispose();
//                    HOperatorSet.FillUp(ho_RegionErosion, out ho_RegionTb);
//
//                    hv_ObjectModel3DSelected.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RegionTb, hv_Om3DScene, "xyz_mapping",
//                        new HTuple(), out hv_ObjectModel3DSelected);
//                    hv_ObjectModel3DAdv.Dispose();
//                    HOperatorSet.CopyObjectModel3d(hv_ObjectModel3DSelected, "all", out hv_ObjectModel3DAdv);
//                    ho_X1.Dispose(); ho_Y1.Dispose(); ho_Z1.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1, out ho_Y1, out ho_Z1, hv_ObjectModel3DAdv, "from_xyz_map", new HTuple(), new HTuple());
//
//
//                    //气缸区域
//                    ho_ROI.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_ROI, 691.782, 863.44, 1097.1, 1236.79);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.Intersection(ho_ROI, ho_Z1, out ExpTmpOutVar_0);
//                        ho_ROI.Dispose();
//                        ho_ROI = ExpTmpOutVar_0;
//                    }
//                    hv_Alpha.Dispose(); hv_Beta.Dispose(); hv_Gamma.Dispose();
//                    HOperatorSet.FitSurfaceFirstOrder(ho_ROI, ho_Z1, "tukey", 5, 2, out hv_Alpha,
//                        out hv_Beta, out hv_Gamma);
//                    hv_Area.Dispose(); hv_Row.Dispose(); hv_Column.Dispose();
//                    HOperatorSet.AreaCenter(ho_ROI, out hv_Area, out hv_Row, out hv_Column);
//                    hv_Width.Dispose(); hv_Height.Dispose();
//                    HOperatorSet.GetImageSize(ho_Z1, out hv_Width, out hv_Height);
//                    ho_ImageSurface.Dispose();
//                    HOperatorSet.GenImageSurfaceFirstOrder(out ho_ImageSurface, "real", hv_Alpha,
//                        hv_Beta, hv_Gamma, hv_Row, hv_Column, hv_Width, hv_Height);
//                    ho_ImageSub.Dispose();
//                    HOperatorSet.SubImage(ho_Z1, ho_ImageSurface, out ho_ImageSub, -1, 0);
//
//                    HOperatorSet.WriteImage(ho_Z1, "tiff", 0, @"D:\\lins\\" + @"ho_Z1");
//
//
//
//                    ho_Region.Dispose();
//                    HOperatorSet.Threshold(ho_ImageSub, out ho_Region, 10, 100);
//                    ho_RegionFillUp.Dispose();
//                    HOperatorSet.FillUp(ho_Region, out ho_RegionFillUp);
//                    ho_RegionClosing.Dispose();
//                    HOperatorSet.ClosingRectangle1(ho_RegionFillUp, out ho_RegionClosing, 51,
//                        51);
//                    ho_ConnectedRegions.Dispose();
//                    HOperatorSet.Connection(ho_RegionClosing, out ho_ConnectedRegions);
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose(); hv_Diameter.Dispose();
//                    HOperatorSet.DiameterRegion(ho_ConnectedRegions, out hv_Row1, out hv_Column1,
//                        out hv_Row2, out hv_Column2, out hv_Diameter);
//                    hv_Rectangularity.Dispose();
//                    HOperatorSet.Rectangularity(ho_ConnectedRegions, out hv_Rectangularity);
//
//                    ho_SelectedRegions.Dispose();
//                    HOperatorSet.SelectShape(ho_ConnectedRegions, out ho_SelectedRegions, (new HTuple("max_diameter")).TupleConcat(
//                        "rectangularity"), "and", (new HTuple(80)).TupleConcat(0.7), (new HTuple(150)).TupleConcat(
//                            1));
//                    ho_RegionOpening.Dispose();
//                    HOperatorSet.OpeningRectangle1(ho_SelectedRegions, out ho_RegionOpening,
//                        5, 5);
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RegionOpening, out hv_Row1, out hv_Column1,
//                        out hv_Row2, out hv_Column2);
//                    ho_RectangleQg.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RectangleQg, hv_Row1, hv_Column1, hv_Row2,
//                        hv_Column2);
//
//
//
//                    //子区域划分
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RegionTb, out hv_Row1, out hv_Column1,
//                        out hv_Row2, out hv_Column2);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_RectangleL.Dispose();
//                        HOperatorSet.GenRectangle1(out ho_RectangleL, hv_Row1 - 100, hv_Column1 - 100,
//                            hv_Row2 + 100, hv_Column1 + 200);
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_RectangleR.Dispose();
//                        HOperatorSet.GenRectangle1(out ho_RectangleR, hv_Row1 - 100, hv_Column2 - 200,
//                            hv_Row2 + 100, hv_Column2 + 100);
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_RectangleU.Dispose();
//                        HOperatorSet.GenRectangle1(out ho_RectangleU, hv_Row1 - 100, hv_Column1 - 100,
//                            hv_Row1 + 150, hv_Column2 + 100);
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_RectangleD.Dispose();
//                        HOperatorSet.GenRectangle1(out ho_RectangleD, hv_Row2 - 150, hv_Column1 - 100,
//                            hv_Row2 + 100, hv_Column2 + 100);
//                    }
//                    ho_RegionDifference.Dispose();
//                    HOperatorSet.Difference(ho_RectangleU, ho_RectangleL, out ho_RegionDifference
//                    );
//                    ho_RectangleU.Dispose();
//                    HOperatorSet.Difference(ho_RegionDifference, ho_RectangleR, out ho_RectangleU
//                    );
//                    ho_RegionDifference.Dispose();
//                    HOperatorSet.Difference(ho_RectangleD, ho_RectangleL, out ho_RegionDifference
//                    );
//                    ho_RectangleD.Dispose();
//                    HOperatorSet.Difference(ho_RegionDifference, ho_RectangleR, out ho_RectangleD);
//
//
//                    ho_RectangleQgL.Dispose();
//                    HOperatorSet.Intersection(ho_RectangleL, ho_RectangleQg, out ho_RectangleQgL);
//                    ho_RectangleQgR.Dispose();
//                    HOperatorSet.Intersection(ho_RectangleR, ho_RectangleQg, out ho_RectangleQgR);
//                    ho_RectangleQgU.Dispose();
//                    HOperatorSet.Intersection(ho_RectangleU, ho_RectangleQg, out ho_RectangleQgU);
//                    ho_RectangleQgD.Dispose();
//                    HOperatorSet.Intersection(ho_RectangleD, ho_RectangleQg, out ho_RectangleQgD);
//
//
//
//
//                    hv_fQgOffsetL.Dispose();
//                    hv_fQgOffsetL = /*25*/spara1.fQgOffsetL;
//                    hv_fQgOffsetR.Dispose();
//                    hv_fQgOffsetR = /*25*/spara1.fQgOffsetR;
//                    hv_fQgOffsetU.Dispose();
//                    hv_fQgOffsetU =/* 25*/spara1.fQgOffsetU;
//                    hv_fQgOffsetD.Dispose();
//                    hv_fQgOffsetD = /*25*/spara1.fQgOffsetD;
//
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleQgL, out hv_Row1, out hv_Column1, out hv_Row2, out hv_Column2);
//                    hv_ColumnL.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_ColumnL = hv_Column2 + hv_fQgOffsetL;
//                    }
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleL, out hv_Row1, out hv_Column1, out hv_Row2, out hv_Column2);
//                    ho_RectangleLAdv.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RectangleLAdv, hv_Row1, hv_Column1, hv_Row2, hv_ColumnL);
//
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleQgR, out hv_Row1, out hv_Column1, out hv_Row2, out hv_Column2);
//                    hv_ColumnR.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_ColumnR = hv_Column1 - hv_fQgOffsetR;
//                    }
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleR, out hv_Row1, out hv_Column1, out hv_Row2, out hv_Column2);
//                    ho_RectangleRAdv.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RectangleRAdv, hv_Row1, hv_ColumnR, hv_Row2, hv_Column2);
//
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleQgU, out hv_Row1, out hv_Column1, out hv_Row2, out hv_Column2);
//                    hv_RowU.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_RowU = hv_Row2 + hv_fQgOffsetU;
//                    }
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleU, out hv_Row1, out hv_Column1,
//                        out hv_Row2, out hv_Column2);
//                    ho_RectangleUAdv.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RectangleUAdv, hv_Row1, hv_ColumnL, hv_RowU,
//                        hv_ColumnR);
//
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleQgD, out hv_Row1, out hv_Column1,
//                        out hv_Row2, out hv_Column2);
//                    hv_RowD.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_RowD = hv_Row1 - hv_fQgOffsetD;
//                    }
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_RectangleD, out hv_Row1, out hv_Column1,
//                        out hv_Row2, out hv_Column2);
//                    ho_RectangleDAdv.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RectangleDAdv, hv_RowD, hv_ColumnL, hv_Row2, hv_ColumnR);
//
//
//                    ho_RectangleCAdv.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RectangleCAdv, hv_RowU, hv_ColumnL, hv_RowD, hv_ColumnR);
//
//                    ho_RectanglePartList.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RectanglePartList);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectanglePartList, ho_RectangleCAdv, out ExpTmpOutVar_0);
//                        ho_RectanglePartList.Dispose();
//                        ho_RectanglePartList = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectanglePartList, ho_RectangleLAdv, out ExpTmpOutVar_0
//                        );
//                        ho_RectanglePartList.Dispose();
//                        ho_RectanglePartList = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectanglePartList, ho_RectangleRAdv, out ExpTmpOutVar_0
//                        );
//                        ho_RectanglePartList.Dispose();
//                        ho_RectanglePartList = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectanglePartList, ho_RectangleUAdv, out ExpTmpOutVar_0
//                        );
//                        ho_RectanglePartList.Dispose();
//                        ho_RectanglePartList = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectanglePartList, ho_RectangleDAdv, out ExpTmpOutVar_0
//                        );
//                        ho_RectanglePartList.Dispose();
//                        ho_RectanglePartList = ExpTmpOutVar_0;
//                    }
//
//
//                    //气缸排序
//                    ho_RectangleQgSort.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RectangleQgSort);
//                    ho_ConnectedRegions.Dispose();
//                    HOperatorSet.Connection(ho_RectangleQgU, out ho_ConnectedRegions);
//                    ho_SortedRegions.Dispose();
//                    HOperatorSet.SortRegion(ho_ConnectedRegions, out ho_SortedRegions, "first_point",
//                        "false", "column");
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectangleQgSort, ho_SortedRegions, out ExpTmpOutVar_0
//                        );
//                        ho_RectangleQgSort.Dispose();
//                        ho_RectangleQgSort = ExpTmpOutVar_0;
//                    }
//
//                    ho_ConnectedRegions.Dispose();
//                    HOperatorSet.Connection(ho_RectangleQgL, out ho_ConnectedRegions);
//                    ho_SortedRegions.Dispose();
//                    HOperatorSet.SortRegion(ho_ConnectedRegions, out ho_SortedRegions, "first_point",
//                        "true", "row");
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectangleQgSort, ho_SortedRegions, out ExpTmpOutVar_0
//                        );
//                        ho_RectangleQgSort.Dispose();
//                        ho_RectangleQgSort = ExpTmpOutVar_0;
//                    }
//
//
//                    ho_ConnectedRegions.Dispose();
//                    HOperatorSet.Connection(ho_RectangleQgD, out ho_ConnectedRegions);
//                    ho_SortedRegions.Dispose();
//                    HOperatorSet.SortRegion(ho_ConnectedRegions, out ho_SortedRegions, "first_point",
//                        "true", "column");
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectangleQgSort, ho_SortedRegions, out ExpTmpOutVar_0
//                        );
//                        ho_RectangleQgSort.Dispose();
//                        ho_RectangleQgSort = ExpTmpOutVar_0;
//                    }
//
//                    ho_ConnectedRegions.Dispose();
//                    HOperatorSet.Connection(ho_RectangleQgR, out ho_ConnectedRegions);
//                    ho_SortedRegions.Dispose();
//                    HOperatorSet.SortRegion(ho_ConnectedRegions, out ho_SortedRegions, "first_point",
//                        "false", "row");
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RectangleQgSort, ho_SortedRegions, out ExpTmpOutVar_0
//                        );
//                        ho_RectangleQgSort.Dispose();
//                        ho_RectangleQgSort = ExpTmpOutVar_0;
//                    }
//
//
//                    //气缸排序2
//
//                    ho_RectangleQgSort.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RectangleQgSort);
//                    ho_RegionQgReal.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionQgReal);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgReal, ho_RectangleQgU, out ExpTmpOutVar_0
//                        );
//                        ho_RegionQgReal.Dispose();
//                        ho_RegionQgReal = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgReal, ho_RectangleQgR, out ExpTmpOutVar_0
//                        );
//                        ho_RegionQgReal.Dispose();
//                        ho_RegionQgReal = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgReal, ho_RectangleQgD, out ExpTmpOutVar_0
//                        );
//                        ho_RegionQgReal.Dispose();
//                        ho_RegionQgReal = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionQgReal, ho_RectangleQgL, out ExpTmpOutVar_0
//                        );
//                        ho_RegionQgReal.Dispose();
//                        ho_RegionQgReal = ExpTmpOutVar_0;
//                    }
//
//                    hv_Number1.Dispose();
//                    HOperatorSet.CountObj(ho_RegionQgIn, out hv_Number1);
//                    hv_Number2.Dispose();
//                    HOperatorSet.CountObj(ho_RegionQgReal, out hv_Number2);
//                    HTuple end_val390 = hv_Number1;
//                    HTuple step_val390 = 1;
//                    for (hv_i = 1; hv_i.Continue(end_val390, step_val390); hv_i = hv_i.TupleAdd(step_val390))
//                    {
//                        ho_ObjectSelected1.Dispose();
//                        HOperatorSet.SelectObj(ho_RegionQgIn, out ho_ObjectSelected1, hv_i);
//
//                        hv_bFind.Dispose();
//                        hv_bFind = 0;
//                        HTuple end_val394 = hv_Number2;
//                        HTuple step_val394 = 1;
//                        for (hv_j = 1; hv_j.Continue(end_val394, step_val394); hv_j = hv_j.TupleAdd(step_val394))
//                        {
//                            ho_ObjectSelected2.Dispose();
//                            HOperatorSet.SelectObj(ho_RegionQgReal, out ho_ObjectSelected2, hv_j);
//
//                            ho_RegionIntersection.Dispose();
//                            HOperatorSet.Intersection(ho_ObjectSelected2, ho_ObjectSelected1, out ho_RegionIntersection
//                            );
//                            hv_Area.Dispose(); hv_Row.Dispose(); hv_Column.Dispose();
//                            HOperatorSet.AreaCenter(ho_RegionIntersection, out hv_Area, out hv_Row,
//                                out hv_Column);
//                            if ((int)(new HTuple(hv_Area.TupleGreater(100))) != 0)
//                            {
//                                hv_bFind.Dispose();
//                                hv_bFind = 1;
//                                {
//                                    HObject ExpTmpOutVar_0;
//                                    HOperatorSet.ConcatObj(ho_RectangleQgSort, ho_ObjectSelected1, out ExpTmpOutVar_0
//                                    );
//                                    ho_RectangleQgSort.Dispose();
//                                    ho_RectangleQgSort = ExpTmpOutVar_0;
//                                }
//                                break;
//                            }
//
//
//                        }
//
//                        if ((int)(new HTuple(hv_bFind.TupleEqual(0))) != 0)
//                        {
//                            ho_EmptyRegion.Dispose();
//                            HOperatorSet.GenEmptyRegion(out ho_EmptyRegion);
//                            {
//                                HObject ExpTmpOutVar_0;
//                                HOperatorSet.ConcatObj(ho_RectangleQgSort, ho_EmptyRegion, out ExpTmpOutVar_0
//                                );
//                                ho_RectangleQgSort.Dispose();
//                                ho_RectangleQgSort = ExpTmpOutVar_0;
//                            }
//                        }
//
//
//                    }
//
//
//
//                    //***************************************************************************************************
//                    //step2  得到整版的粒子高度分布图
//                    //提取粒子高度区域 包含气缸 分区提取
//
//
//                    hv_Width.Dispose(); hv_Height.Dispose();
//                    HOperatorSet.GetImageSize(ho_Z1, out hv_Width, out hv_Height);
//                    ho_ImageSubZ1.Dispose();
//                    HOperatorSet.GenImageConst(out ho_ImageSubZ1, "real", hv_Width, hv_Height);
//                    ho_ImageZ1ZeroReal.Dispose();
//                    HOperatorSet.GenImageConst(out ho_ImageZ1ZeroReal, "real", hv_Width, hv_Height);
//
//                    //中间区域粒子提取
//                    hv_Om3DC.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleCAdv, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DC);
//
//                    hv_SampledObjectModel3D.Dispose();
//                    HOperatorSet.SampleObjectModel3d(hv_Om3DC, "fast", 5, new HTuple(), new HTuple(),
//                        out hv_SampledObjectModel3D);
//
//                    hv_OM3DPlane.Dispose();
//                    HOperatorSet.CopyObjectModel3d(hv_SampledObjectModel3D, "all", out hv_OM3DPlane);
//                    hv_ParFitting.Dispose();
//                    hv_ParFitting = new HTuple();
//                    hv_ParFitting[0] = "primitive_type";
//                    hv_ParFitting[1] = "fitting_algorithm";
//                    hv_ValFitting.Dispose();
//                    hv_ValFitting = new HTuple();
//                    hv_ValFitting[0] = "plane";
//                    hv_ValFitting[1] = "least_squares_tukey";
//                    hv_ObjectModel3DOutID.Dispose();
//                    HOperatorSet.FitPrimitivesObjectModel3d(hv_OM3DPlane, hv_ParFitting, hv_ValFitting,
//                        out hv_ObjectModel3DOutID);
//                    hv_GenParamPosePlane.Dispose();
//                    HOperatorSet.GetObjectModel3dParams(hv_ObjectModel3DOutID, "primitive_pose",
//                        out hv_GenParamPosePlane);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_PlaneDatum.Dispose();
//                        HOperatorSet.GenPlaneObjectModel3d(hv_GenParamPosePlane, (((new HTuple(-1)).TupleConcat(
//                            -1)).TupleConcat(1)).TupleConcat(1) * 900, (((new HTuple(-1)).TupleConcat(
//                                1)).TupleConcat(1)).TupleConcat(-1) * 900, out hv_PlaneDatum);
//                    }
//
//
//                    hv_PoseTbC.Dispose();
//                    new HVisionAdv().trans_pose_face_x(hv_GenParamPosePlane, 0, out hv_PoseTbC);
//
//
//                    hv_PoseInvert.Dispose();
//                    HOperatorSet.PoseInvert(hv_PoseTbC, out hv_PoseInvert);
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseInvert, out hv_HomMat3D);
//                    hv_OM3dPZeroC.Dispose();
//                    HOperatorSet.AffineTransObjectModel3d(hv_Om3DC, hv_HomMat3D, out hv_OM3dPZeroC);
//
//                    ho_X1PZeroC.Dispose(); ho_Y1PZeroC.Dispose(); ho_Z1PZeroC.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1PZeroC, out ho_Y1PZeroC, out ho_Z1PZeroC, hv_OM3dPZeroC, "from_xyz_map", new HTuple(), new HTuple());
//
//
//                    //用中间区域的调平矩阵调平整个面板
//                    hv_OM3dPZero.Dispose();
//                    HOperatorSet.AffineTransObjectModel3d(hv_ObjectModel3DAdv, hv_HomMat3D, out hv_OM3dPZero);
//                    ho_X1PZero.Dispose(); ho_Y1PZero.Dispose(); ho_Z1PZero.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1PZero, out ho_Y1PZero, out ho_Z1PZero,
//                        hv_OM3dPZero, "from_xyz_map", new HTuple(), new HTuple());
//
//
//                    hv_fThBulgeLower.Dispose();
//                    hv_fThBulgeLower = /*1.5*/spara1.fThBulgeLower;
//                    hv_fThBulgeHiger.Dispose();
//                    hv_fThBulgeHiger =/* 3*/spara1.fThBulgeHiger;
//
//                    ho_RegionRoiCBulge.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiCBulge);
//                    ho_RegionRoiCBulge.Dispose(); ho_ImageSubC.Dispose();
//                    get_plane_ranger_z_out_region_x(ho_Z1PZeroC, out ho_RegionRoiCBulge, out ho_ImageSubC,
//                        out ho_ZZeroRealC, hv_fThBulgeLower, hv_fThBulgeHiger, 50, 61, 61, 41);
//
//                    ho_RegionRoiCBulgeUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiCBulge, out ho_RegionRoiCBulgeUnion);
//
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionRoiCBulgeUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubC, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealC, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//                    //气缸区域粒子提取-L
//
//                    hv_fQgHOrg.Dispose();
//                    hv_fQgHOrg = /*18.0*/spara1.fQgHOrg;
//
//                    hv_fQgExCol.Dispose();
//                    hv_fQgExCol = /*15*/spara1.fQgExCol;
//                    hv_fQgExRow.Dispose();
//                    hv_fQgExRow = /*9*/spara1.fQgExRow;
//
//
//                    hv_fQgThOffset.Dispose();
//                    hv_fQgThOffset = /*3*/spara1.fQgThOffset;
//
//                    hv_Om3DL.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleLAdv, hv_ObjectModel3DAdv, "xyz_mapping", new HTuple(), out hv_Om3DL);
//
//                    ho_RectangleQgEx.Dispose();
//                    HOperatorSet.DilationRectangle1(ho_RectangleQg, out ho_RectangleQgEx, hv_fQgExCol, hv_fQgExRow);
//
//                    ho_RectangleLAdvRemoveQg.Dispose();
//                    HOperatorSet.Difference(ho_RectangleLAdv, ho_RectangleQgEx, out ho_RectangleLAdvRemoveQg);
//                    hv_Om3DLRemoveQg.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleLAdvRemoveQg, hv_ObjectModel3DAdv, "xyz_mapping", new HTuple(), out hv_Om3DLRemoveQg);
//
//
//                    hv_PoseInvert.Dispose();
//                    HOperatorSet.PoseInvert(hv_PoseTbC, out hv_PoseInvert);
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseInvert, out hv_HomMat3D);
//                    hv_OM3dPZeroL.Dispose();
//                    HOperatorSet.AffineTransObjectModel3d(hv_Om3DL, hv_HomMat3D, out hv_OM3dPZeroL);
//
//                    ho_X1PZeroL.Dispose(); ho_Y1PZeroL.Dispose(); ho_Z1PZeroL.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1PZeroL, out ho_Y1PZeroL, out ho_Z1PZeroL,
//                        hv_OM3dPZeroL, "from_xyz_map", new HTuple(), new HTuple());
//
//
//                    ho_RegionDifference.Dispose();
//                    HOperatorSet.Difference(ho_Z1PZeroL, ho_RectangleQgEx, out ho_RegionDifference);
//                    ho_Z1PZeroLRemoveQg.Dispose();
//                    HOperatorSet.ReduceDomain(ho_Z1PZeroL, ho_RegionDifference, out ho_Z1PZeroLRemoveQg);
//                    ho_RegionQgExL.Dispose();
//                    HOperatorSet.Intersection(ho_Z1PZeroL, ho_RectangleQgEx, out ho_RegionQgExL);
//
//
//
//                    ho_RegionRoiLBulgeRemoveQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiLBulgeRemoveQg);
//                    ho_RegionRoiLBulgeRemoveQg.Dispose(); ho_ImageSubLRemoveQg.Dispose();
//                    get_plane_ranger_z_out_region_x(ho_Z1PZeroLRemoveQg, out ho_RegionRoiLBulgeRemoveQg,
//                        out ho_ImageSubLRemoveQg, out ho_ZZeroRealL, hv_fThBulgeLower, hv_fThBulgeHiger,
//                        50, 61, 61, 41);
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiLBulgeRemoveQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubLRemoveQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealL, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//
//                    ho_RegionRoiLBulgeQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiLBulgeQg);
//                    ho_ImageSubLQg.Dispose(); ho_RegionRoiLBulgeQg.Dispose();
//                    get_qg_z_out_region_x(ho_Z1PZeroL, ho_RegionQgExL, out ho_ImageSubLQg, out ho_RegionRoiLBulgeQg,
//                        out ho_ZZeroRealLQg, hv_fQgHOrg, hv_fQgThOffset, 100);
//
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiLBulgeQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubLQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealLQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//
//
//
//                    //气缸区域粒子提取-R
//
//                    hv_Om3DR.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleRAdv, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DR);
//
//                    ho_RegionIntersection.Dispose();
//                    HOperatorSet.Intersection(ho_RectangleQg, ho_RectangleRAdv, out ho_RegionIntersection
//                    );
//
//
//                    ho_RegionMoved.Dispose();
//                    HOperatorSet.MoveRegion(ho_RegionIntersection, out ho_RegionMoved, 0, 20);
//                    ho_RectangleQgEx.Dispose();
//                    HOperatorSet.Union2(ho_RegionIntersection, ho_RegionMoved, out ho_RectangleQgEx
//                    );
//
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.DilationRectangle1(ho_RectangleQgEx, out ExpTmpOutVar_0, hv_fQgExCol,
//                            hv_fQgExRow);
//                        ho_RectangleQgEx.Dispose();
//                        ho_RectangleQgEx = ExpTmpOutVar_0;
//                    }
//
//
//                    ho_RectangleRAdvRemoveQg.Dispose();
//                    HOperatorSet.Difference(ho_RectangleRAdv, ho_RectangleQgEx, out ho_RectangleRAdvRemoveQg
//                    );
//                    hv_Om3DRRemoveQg.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleRAdvRemoveQg, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DRRemoveQg);
//
//
//                    hv_PoseInvert.Dispose();
//                    HOperatorSet.PoseInvert(hv_PoseTbC, out hv_PoseInvert);
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseInvert, out hv_HomMat3D);
//                    hv_OM3dPZeroR.Dispose();
//                    HOperatorSet.AffineTransObjectModel3d(hv_Om3DR, hv_HomMat3D, out hv_OM3dPZeroR);
//
//                    ho_X1PZeroR.Dispose(); ho_Y1PZeroR.Dispose(); ho_Z1PZeroR.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1PZeroR, out ho_Y1PZeroR, out ho_Z1PZeroR,
//                        hv_OM3dPZeroR, "from_xyz_map", new HTuple(), new HTuple());
//
//
//
//
//                    ho_RegionDifference.Dispose();
//                    HOperatorSet.Difference(ho_Z1PZeroR, ho_RectangleQgEx, out ho_RegionDifference);
//                    ho_Z1PZeroRRemoveQg.Dispose();
//                    HOperatorSet.ReduceDomain(ho_Z1PZeroR, ho_RegionDifference, out ho_Z1PZeroRRemoveQg);
//                    ho_RegionQgExR.Dispose();
//                    HOperatorSet.Intersection(ho_Z1PZeroR, ho_RectangleQgEx, out ho_RegionQgExR);
//
//
//                    ho_RegionRoiRBulgeRemoveQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiRBulgeRemoveQg);
//                    ho_RegionRoiRBulgeRemoveQg.Dispose(); ho_ImageSubRRemoveQg.Dispose();
//                    get_plane_ranger_z_out_region_x(ho_Z1PZeroRRemoveQg, out ho_RegionRoiRBulgeRemoveQg,
//                        out ho_ImageSubRRemoveQg, out ho_ZZeroRealR, hv_fThBulgeLower, hv_fThBulgeHiger,
//                        50, 61, 61, 41);
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiRBulgeRemoveQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubRRemoveQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealR, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//                    ho_RegionRoiRBulgeQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiRBulgeQg);
//                    ho_ImageSubRQg.Dispose(); ho_RegionRoiRBulgeQg.Dispose();
//                    get_qg_z_out_region_x(ho_Z1PZeroR, ho_RegionQgExR, out ho_ImageSubRQg, out ho_RegionRoiRBulgeQg,
//                        out ho_ZZeroRealRQg, hv_fQgHOrg, hv_fQgThOffset, 100);
//
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiRBulgeQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubRQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealRQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//
//                    //气缸区域粒子提取-U
//                    hv_Om3DU.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleUAdv, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DU);
//
//                    ho_RectangleQgEx.Dispose();
//                    HOperatorSet.DilationRectangle1(ho_RectangleQg, out ho_RectangleQgEx, hv_fQgExRow,
//                        hv_fQgExCol);
//
//                    ho_RectangleUAdvRemoveQg.Dispose();
//                    HOperatorSet.Difference(ho_RectangleUAdv, ho_RectangleQgEx, out ho_RectangleUAdvRemoveQg
//                    );
//                    hv_Om3DURemoveQg.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleUAdvRemoveQg, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DURemoveQg);
//
//
//                    hv_PoseInvert.Dispose();
//                    HOperatorSet.PoseInvert(hv_PoseTbC, out hv_PoseInvert);
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseInvert, out hv_HomMat3D);
//                    hv_OM3dPZeroU.Dispose();
//                    HOperatorSet.AffineTransObjectModel3d(hv_Om3DU, hv_HomMat3D, out hv_OM3dPZeroU);
//
//                    ho_X1PZeroU.Dispose(); ho_Y1PZeroU.Dispose(); ho_Z1PZeroU.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1PZeroU, out ho_Y1PZeroU, out ho_Z1PZeroU,
//                        hv_OM3dPZeroU, "from_xyz_map", new HTuple(), new HTuple());
//
//
//
//
//                    ho_RegionDifference.Dispose();
//                    HOperatorSet.Difference(ho_Z1PZeroU, ho_RectangleQgEx, out ho_RegionDifference);
//                    ho_Z1PZeroURemoveQg.Dispose();
//                    HOperatorSet.ReduceDomain(ho_Z1PZeroU, ho_RegionDifference, out ho_Z1PZeroURemoveQg);
//                    ho_RegionQgExU.Dispose();
//                    HOperatorSet.Intersection(ho_Z1PZeroU, ho_RectangleQgEx, out ho_RegionQgExU);
//
//
//
//
//                    ho_RegionRoiUBulgeRemoveQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiUBulgeRemoveQg);
//                    ho_RegionRoiUBulgeRemoveQg.Dispose(); ho_ImageSubURemoveQg.Dispose();
//                    get_plane_ranger_z_out_region_x(ho_Z1PZeroURemoveQg, out ho_RegionRoiUBulgeRemoveQg,
//                        out ho_ImageSubURemoveQg, out ho_ZZeroRealU, hv_fThBulgeLower, hv_fThBulgeHiger,
//                        50, 61, 61, 41);
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiUBulgeRemoveQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubURemoveQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealU, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//                    ho_RegionRoiUBulgeQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiUBulgeQg);
//                    ho_ImageSubUQg.Dispose(); ho_RegionRoiUBulgeQg.Dispose();
//                    get_qg_z_out_region_x(ho_Z1PZeroU, ho_RegionQgExU, out ho_ImageSubUQg, out ho_RegionRoiUBulgeQg,
//                        out ho_ZZeroRealUQg, hv_fQgHOrg, hv_fQgThOffset, 100);
//
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiUBulgeQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubUQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealUQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//
//                    //气缸区域粒子提取-D
//                    hv_Om3DD.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleDAdv, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DD);
//
//                    ho_RectangleQgEx.Dispose();
//                    HOperatorSet.DilationRectangle1(ho_RectangleQg, out ho_RectangleQgEx, hv_fQgExRow,
//                        hv_fQgExCol);
//
//                    ho_RectangleDAdvRemoveQg.Dispose();
//                    HOperatorSet.Difference(ho_RectangleDAdv, ho_RectangleQgEx, out ho_RectangleDAdvRemoveQg
//                    );
//                    hv_Om3DDRemoveQg.Dispose();
//                    HOperatorSet.ReduceObjectModel3dByView(ho_RectangleDAdvRemoveQg, hv_ObjectModel3DAdv,
//                        "xyz_mapping", new HTuple(), out hv_Om3DDRemoveQg);
//
//
//                    hv_PoseInvert.Dispose();
//                    HOperatorSet.PoseInvert(hv_PoseTbC, out hv_PoseInvert);
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseInvert, out hv_HomMat3D);
//                    hv_OM3dPZeroD.Dispose();
//                    HOperatorSet.AffineTransObjectModel3d(hv_Om3DD, hv_HomMat3D, out hv_OM3dPZeroD);
//
//                    ho_X1PZeroD.Dispose(); ho_Y1PZeroD.Dispose(); ho_Z1PZeroD.Dispose();
//                    HOperatorSet.ObjectModel3dToXyz(out ho_X1PZeroD, out ho_Y1PZeroD, out ho_Z1PZeroD, hv_OM3dPZeroD, "from_xyz_map", new HTuple(), new HTuple());
//
//                    ho_RegionDifference.Dispose();
//                    HOperatorSet.Difference(ho_Z1PZeroD, ho_RectangleQgEx, out ho_RegionDifference);
//                    ho_Z1PZeroDRemoveQg.Dispose();
//                    HOperatorSet.ReduceDomain(ho_Z1PZeroD, ho_RegionDifference, out ho_Z1PZeroDRemoveQg);
//                    ho_RegionQgExD.Dispose();
//                    HOperatorSet.Intersection(ho_Z1PZeroD, ho_RectangleQgEx, out ho_RegionQgExD);
//
//
//                    ho_RegionRoiDBulgeRemoveQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiDBulgeRemoveQg);
//                    ho_RegionRoiDBulgeRemoveQg.Dispose(); ho_ImageSubDRemoveQg.Dispose();
//                    get_plane_ranger_z_out_region_x(ho_Z1PZeroDRemoveQg, out ho_RegionRoiDBulgeRemoveQg,
//                        out ho_ImageSubDRemoveQg, out ho_ZZeroRealD, hv_fThBulgeLower, hv_fThBulgeHiger,
//                        50, 61, 61, 41);
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiDBulgeRemoveQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubDRemoveQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealD, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//
//
//                    ho_RegionRoiDBulgeQg.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiDBulgeQg);
//                    ho_ImageSubDQg.Dispose(); ho_RegionRoiDBulgeQg.Dispose();
//                    get_qg_z_out_region_x(ho_Z1PZeroD, ho_RegionQgExD, out ho_ImageSubDQg, out ho_RegionRoiDBulgeQg,
//                        out ho_ZZeroRealDQg, hv_fQgHOrg, hv_fQgThOffset, 100);
//
//
//
//                    ho_RegionUnion.Dispose();
//                    HOperatorSet.Union1(ho_RegionRoiDBulgeQg, out ho_RegionUnion);
//                    hv_Rows.Dispose(); hv_Columns.Dispose();
//                    HOperatorSet.GetRegionPoints(ho_RegionUnion, out hv_Rows, out hv_Columns);
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ImageSubDQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageSubZ1, hv_Rows, hv_Columns, hv_Grayval);
//
//                    hv_Grayval.Dispose();
//                    HOperatorSet.GetGrayval(ho_ZZeroRealDQg, hv_Rows, hv_Columns, out hv_Grayval);
//                    HOperatorSet.SetGrayval(ho_ImageZ1ZeroReal, hv_Rows, hv_Columns, hv_Grayval);
//
//                    //气缸区域合并一下
//                    ho_RegionRoiLBulge.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiLBulge);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiLBulge, ho_RegionRoiLBulgeRemoveQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiLBulge.Dispose();
//                        ho_RegionRoiLBulge = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiLBulge, ho_RegionRoiLBulgeQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiLBulge.Dispose();
//                        ho_RegionRoiLBulge = ExpTmpOutVar_0;
//                    }
//
//                    ho_RegionRoiRBulge.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiRBulge);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiRBulge, ho_RegionRoiRBulgeRemoveQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiRBulge.Dispose();
//                        ho_RegionRoiRBulge = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiRBulge, ho_RegionRoiRBulgeQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiRBulge.Dispose();
//                        ho_RegionRoiRBulge = ExpTmpOutVar_0;
//                    }
//
//
//                    ho_RegionRoiUBulge.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiUBulge);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiUBulge, ho_RegionRoiUBulgeRemoveQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiUBulge.Dispose();
//                        ho_RegionRoiUBulge = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiUBulge, ho_RegionRoiUBulgeQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiUBulge.Dispose();
//                        ho_RegionRoiUBulge = ExpTmpOutVar_0;
//                    }
//
//                    ho_RegionRoiDBulge.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionRoiDBulge);
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiDBulge, ho_RegionRoiDBulgeRemoveQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiDBulge.Dispose();
//                        ho_RegionRoiDBulge = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionRoiDBulge, ho_RegionRoiDBulgeQg, out ExpTmpOutVar_0
//                        );
//                        ho_RegionRoiDBulge.Dispose();
//                        ho_RegionRoiDBulge = ExpTmpOutVar_0;
//                    }
//
//
//                    //区域聚类合并 矩形化
//
//                    hv_fConnectionDis.Dispose();
//                    hv_fConnectionDis = /*50*/spara1.fConnectionDis;
//
//
//                    //非气缸区域
//                    ho_RegionPartLzC.Dispose(); ho_RectPartLzC.Dispose();
//                    new HVisionAdv().connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiCBulge, out ho_RegionPartLzC, out ho_RectPartLzC, hv_fConnectionDis);
//
//                    //气缸区域
//                    //采用合并后的气缸区域一起进行离散分割
//                    ho_RegionPartLzL.Dispose(); ho_RectPartLzL.Dispose();
//                    new HVisionAdv().connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiLBulge, out ho_RegionPartLzL,
//                        out ho_RectPartLzL, hv_fConnectionDis);
//                    ho_RegionPartLzR.Dispose(); ho_RectPartLzR.Dispose();
//                    new HVisionAdv().connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiRBulge, out ho_RegionPartLzR,
//                        out ho_RectPartLzR, hv_fConnectionDis);
//                    ho_RegionPartUzL.Dispose(); ho_RectPartLzU.Dispose();
//                    new HVisionAdv().connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiUBulge, out ho_RegionPartUzL,
//                        out ho_RectPartLzU, hv_fConnectionDis);
//                    ho_RegionPartLzD.Dispose(); ho_RectPartLzD.Dispose();
//                    new HVisionAdv().connection_3d_region_by_dis_x(ho_X1, ho_Y1, ho_Z1, ho_RegionRoiDBulge, out ho_RegionPartLzD,
//                        out ho_RectPartLzD, hv_fConnectionDis);
//
//                    #endregion
//
//                        //结果数据
//
//                        spara2.bTJG = true;
//
//                    spara2.PoseTb = new HTuple(hv_PoseTbC);
//
//
//
//
//                    spara2.X1.Dispose();
//                    if (ho_X1 != null && ho_X1.IsInitialized()) { spara2.X1 = ho_X1.Clone(); };
//                    spara2.Y1.Dispose();
//                    if (ho_Y1 != null && ho_Y1.IsInitialized()) { spara2.Y1 = ho_Y1.Clone(); };
//                    spara2.Z1.Dispose();
//                    if (ho_Z1 != null && ho_Z1.IsInitialized()) { spara2.Z1 = ho_Z1.Clone(); };
//
//
//                    spara2.ImageSubZ1.Dispose();
//                    if (ho_ImageSubZ1 != null && ho_ImageSubZ1.IsInitialized()) { spara2.ImageSubZ1 = ho_ImageSubZ1.Clone(); };
//                    spara2.ImageZ1ZeroReal.Dispose();
//                    if (ho_ImageZ1ZeroReal != null && ho_ImageZ1ZeroReal.IsInitialized()) { spara2.ImageZ1ZeroReal = ho_ImageZ1ZeroReal.Clone(); };
//
//
//                    spara2.Z1PZero.Dispose();
//                    if (ho_Z1PZero != null && ho_Z1PZero.IsInitialized()) { spara2.Z1PZero = ho_Z1PZero.Clone(); };
//                    spara2.X1PZero.Dispose();
//                    if (ho_X1PZero != null && ho_X1PZero.IsInitialized()) { spara2.X1PZero = ho_X1PZero.Clone(); };
//                    spara2.Y1PZero.Dispose();
//                    if (ho_Y1PZeroC != null && ho_Y1PZero.IsInitialized()) { spara2.Y1PZero = ho_Y1PZero.Clone(); };
//
//
//
//                    spara2.RectPartLzC.Dispose();
//                    if (ho_RectPartLzC != null && ho_RectPartLzC.IsInitialized()) { spara2.RectPartLzC = ho_RectPartLzC.Clone(); };
//
//
//                    spara2.RectPartLzU.Dispose();
//                    if (ho_RectPartLzU != null && ho_RectPartLzU.IsInitialized()) { spara2.RectPartLzU = ho_RectPartLzU.Clone(); };
//
//                    spara2.RectPartLzL.Dispose();
//                    if (ho_RectPartLzL != null && ho_RectPartLzL.IsInitialized()) { spara2.RectPartLzL = ho_RectPartLzL.Clone(); };
//
//                    spara2.RectPartLzD.Dispose();
//                    if (ho_RectPartLzD != null && ho_RectPartLzD.IsInitialized()) { spara2.RectPartLzD = ho_RectPartLzD.Clone(); };
//
//                    spara2.RectPartLzR.Dispose();
//                    if (ho_RectPartLzR != null && ho_RectPartLzR.IsInitialized()) { spara2.RectPartLzR = ho_RectPartLzR.Clone(); };
//
//                    spara2.RectangleQgSort.Dispose();
//                    if (ho_RectangleQgSort != null && ho_RectangleQgSort.IsInitialized()) { spara2.RectangleQgSort = ho_RectangleQgSort.Clone(); };
//
//
//                    // 3D
//                    spara2.OM3ImageAdv = new HTuple();
//                    if (hv_ObjectModel3DAdv.Length > 0)
//                    {
//                        try { HOperatorSet.CopyObjectModel3d(hv_ObjectModel3DAdv, "all", out spara2.OM3ImageAdv); }
//                        catch (HalconException ex) { ; }
//
//                    }
//
//                    sError.iCode = 0;
//                    sError.strInfo = "";
//
//                }
//                catch (HalconException ex)
//                {
//                    string str = ex.ToString();
//                    CLogTxt.WriteTxt(str);
//
//                    sError.iCode = -1;
//                    sError.strInfo = "未知异常!";
//                }
//
//
//                break;
//            }
//
//
//        //释放所有临时变量
//
//        HOperatorSet.CountSeconds(out time_end);
//        spara2.time = time_end - time_start;
//        return sError;
//    }
//
//
//    //执行粒子路径规划
//    public s_Rtnf OnLzPP(s_JggyPara spara1, s_DefectPlateBRtsPara spara0, ref s_LzppRtsPara spara2)
//    {
//
//        HTuple time_start = 0.0;
//        HTuple time_end = 0.0;
//        HOperatorSet.CountSeconds(out time_start);
//
//        s_Rtnf sError = new s_Rtnf();
//        sError.iCode = -1;
//        sError.strInfo = "";
//
//
//        //复位结果数据
//        spara2.Reset();
//
//        #region 临时变量
//
//            // Stack for temporary objects 
//            HObject[] OTemp = new HObject[20];
//
//        // Local iconic variables 
//
//        HObject ho_Domain = null, ho_X1 = null, ho_Y1 = null;
//        HObject ho_Z1 = null, ho_RectangleQgSort = null, ho_ImageSubZ1 = null, ho_ImageZ1ZeroReal = null;
//        HObject ho_Z1PZero = null, ho_RectPartLzC = null;
//        HObject ho_X1PZero = null;
//        HObject ho_Y1PZero = null;
//        HObject ho_RectPartLzL = null, ho_RectPartLzR = null, ho_RectPartLzU = null;
//        HObject ho_RectPartLzD = null, ho_RegionMxAllList = null, ho_XYZ1 = null;
//        HObject ho_RectPartLzCUnion = null, ho_RegionMxRoiListC = null;
//        HObject ho_RegionMxRoiList = null, ho_RectPartLzUQgUnion = null;
//        HObject ho_RegionMxRoiListU = null, ho_RectPartLzLQgUnion = null;
//        HObject ho_RegionMxRoiListL = null, ho_RectPartLzDQgUnion = null;
//        HObject ho_RegionMxRoiListD = null, ho_RectPartLzRQgUnion = null;
//        HObject ho_RegionMxRoiListR = null, ho_ptsCross = null, ho_ObjectSelected = null;
//        HObject ho_CrossSel = null, ho_Cross = null, ho_QgNotSafe = null;
//        HObject ho_PtsQgNotSafe = null, ho_Arrow = null;
//        HObject ho_ImageReduced;
//
//        // Local control variables 
//
//        HTuple hv_Min = new HTuple(), hv_Max = new HTuple();
//        HTuple hv_Range = new HTuple(), hv_Row1 = new HTuple();
//        HTuple hv_Column1 = new HTuple(), hv_Row2 = new HTuple();
//        HTuple hv_Column2 = new HTuple(), hv_PoseTb = new HTuple();
//        HTuple hv_HomMat3D = new HTuple(), hv_ptsXListAll = new HTuple();
//        HTuple hv_ptsYListAll = new HTuple(), hv_ptsZListAll = new HTuple();
//        HTuple hv_ptsDefListAll = new HTuple(), hv_ptsRowListAll = new HTuple();
//        HTuple hv_ptsColListAll = new HTuple(), hv_fDjDiamiter = new HTuple();
//        HTuple hv_fJgLzUpOffset = new HTuple(), hv_fJgDpUpOffset = new HTuple();
//        HTuple hv_iModeJgPPZStepMode = new HTuple(), hv_fJgPPZStepFix = new HTuple();
//        HTuple hv_fJgPPZStepK = new HTuple(), hv_fJgPPZStepB = new HTuple();
//        HTuple hv_iModeJgPPYStepMode = new HTuple(), hv_fJgPPYStepFix = new HTuple();
//        HTuple hv_fJgPPYStepK = new HTuple(), hv_iModeJgPPSort = new HTuple();
//        HTuple hv_fJgPPYStepCur = new HTuple(), hv_fYResolution = new HTuple();
//        HTuple hv_iJgPPYStepPixelCur = new HTuple(), hv_ptsXListZeroRoiC = new HTuple();
//        HTuple hv_ptsYListZeroRoiC = new HTuple(), hv_ptsZListZeroRoiC = new HTuple();
//        HTuple hv_ptsDefListZeroRoiC = new HTuple(), hv_ptsRowListRoiC = new HTuple();
//        HTuple hv_ptsColListRoiC = new HTuple(), hv_ptsXListZeroRoiU = new HTuple();
//        HTuple hv_ptsYListZeroRoiU = new HTuple(), hv_ptsZListZeroRoiU = new HTuple();
//        HTuple hv_ptsDefListZeroRoiU = new HTuple(), hv_ptsRowListRoiU = new HTuple();
//        HTuple hv_ptsColListRoiU = new HTuple(), hv_ptsXListZeroRoiL = new HTuple();
//        HTuple hv_ptsYListZeroRoiL = new HTuple(), hv_ptsZListZeroRoiL = new HTuple();
//        HTuple hv_ptsDefListZeroRoiL = new HTuple(), hv_ptsRowListRoiL = new HTuple();
//        HTuple hv_ptsColListRoiL = new HTuple(), hv_ptsXListZeroRoiD = new HTuple();
//        HTuple hv_ptsYListZeroRoiD = new HTuple(), hv_ptsZListZeroRoiD = new HTuple();
//        HTuple hv_ptsDefListZeroRoiD = new HTuple(), hv_ptsRowListRoiD = new HTuple();
//        HTuple hv_ptsColListRoiD = new HTuple(), hv_ptsXListZeroRoiR = new HTuple();
//        HTuple hv_ptsYListZeroRoiR = new HTuple(), hv_ptsZListZeroRoiR = new HTuple();
//        HTuple hv_ptsDefListZeroRoiR = new HTuple(), hv_ptsRowListRoiR = new HTuple();
//        HTuple hv_ptsColListRoiR = new HTuple(), hv_ptsXList = new HTuple();
//        HTuple hv_ptsYList = new HTuple(), hv_ptsZList = new HTuple();
//        HTuple hv_fQgSafeDis = new HTuple(), hv_fResolution = new HTuple();
//        HTuple hv_fQgSafeDisPixel = new HTuple(), hv_ptsQgNotSafeListAll = new HTuple();
//        HTuple hv_iNumQg = new HTuple(), hv_iNumPts = new HTuple();
//        HTuple /*hv_i = new HTuple(), hv_j = new HTuple(), */hv_IsInside = new HTuple();
//        HTuple hv_str = new HTuple(), hv_DistanceMin = new HTuple();
//        HTuple hv_DistanceMax = new HTuple(), hv_Selected = new HTuple();
//        HTuple hv_Substrings = new HTuple(), hv_Index = new HTuple();
//        HTuple hv_Indices = new HTuple(), hv_Sequence = new HTuple();
//        HTuple hv_Reduced = new HTuple(), hv_ptsRowListSel = new HTuple();
//        HTuple hv_ptsColListSel = new HTuple(), hv_Newtuple = new HTuple();
//        HTuple hv_ptsXListAdv = new HTuple(), hv_ptsYListAdv = new HTuple();
//        HTuple hv_ptsZListAdv = new HTuple(), hv_ptsDefListAdv = new HTuple();
//        HTuple hv_ptsRowListAdv = new HTuple(), hv_ptsColListAdv = new HTuple();
//        HTuple hv_ptsQgNotSafeListAdv = new HTuple(), hv_fJgTdZUp = new HTuple();
//
//        HTuple hv_Area = new HTuple();
//        HTuple hv_Row = new HTuple();
//        HTuple hv_Column = new HTuple();
//
//
//        // Initialize local and output iconic variables 
//        HOperatorSet.GenEmptyObj(out ho_Domain);
//        HOperatorSet.GenEmptyObj(out ho_X1);
//        HOperatorSet.GenEmptyObj(out ho_Y1);
//        HOperatorSet.GenEmptyObj(out ho_Z1);
//        HOperatorSet.GenEmptyObj(out ho_RectangleQgSort);
//        HOperatorSet.GenEmptyObj(out ho_ImageSubZ1);
//        HOperatorSet.GenEmptyObj(out ho_ImageZ1ZeroReal);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZero);
//        HOperatorSet.GenEmptyObj(out ho_ImageReduced);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzC);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzL);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzR);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzU);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzD);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxAllList);
//        HOperatorSet.GenEmptyObj(out ho_XYZ1);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzCUnion);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListC);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxRoiList);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzUQgUnion);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListU);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzLQgUnion);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListL);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzDQgUnion);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListD);
//        HOperatorSet.GenEmptyObj(out ho_RectPartLzRQgUnion);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListR);
//        HOperatorSet.GenEmptyObj(out ho_ptsCross);
//        HOperatorSet.GenEmptyObj(out ho_ObjectSelected);
//        HOperatorSet.GenEmptyObj(out ho_CrossSel);
//        HOperatorSet.GenEmptyObj(out ho_Cross);
//        HOperatorSet.GenEmptyObj(out ho_QgNotSafe);
//        HOperatorSet.GenEmptyObj(out ho_PtsQgNotSafe);
//        HOperatorSet.GenEmptyObj(out ho_Arrow);
//
//        HOperatorSet.GenEmptyObj(out ho_X1PZero);
//        HOperatorSet.GenEmptyObj(out ho_Y1PZero);
//
//
//
//
//        #endregion
//
//            while (true)
//            {
//                try
//                {
//
//
//                    //判断输入
//                    if (!spara0.ImageSubZ1.IsInitialized() || spara0.ImageSubZ1.CountObj() == 0)
//                    {
//                        HOperatorSet.CountSeconds(out time_end);
//                        spara2.time = time_end - time_start;
//
//                        sError.iCode = 1;
//                        sError.strInfo = "图像为空!";
//                        break;
//                    }
//
//
//
//                    if (spara0.PoseTb.Length == 0)
//                    {
//                        HOperatorSet.CountSeconds(out time_end);
//                        spara2.time = time_end - time_start;
//
//                        sError.iCode = 1;
//                        sError.strInfo = "变换矩阵异常!";
//                        break;
//                    }
//
//
//                    #region 算法整体部分
//
//                        //输出中间变量
//                        hv_ptsXListAll.Dispose();
//                    hv_ptsXListAll = new HTuple();
//                    hv_ptsYListAll.Dispose();
//                    hv_ptsYListAll = new HTuple();
//                    hv_ptsZListAll.Dispose();
//                    hv_ptsZListAll = new HTuple();
//                    hv_ptsDefListAll.Dispose();
//                    hv_ptsDefListAll = new HTuple();
//
//                    hv_ptsRowListAll.Dispose();
//                    hv_ptsRowListAll = new HTuple();
//                    hv_ptsColListAll.Dispose();
//                    hv_ptsColListAll = new HTuple();
//
//                    ho_RegionMxAllList.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionMxAllList);
//
//
//                    //输入缺陷
//                    hv_PoseTb = new HTuple(spara0.PoseTb);
//
//
//                    ho_X1.Dispose();
//                    if (spara0.X1 != null && spara0.X1.IsInitialized()) { ho_X1 = spara0.X1.Clone(); };
//                    ho_Y1.Dispose();
//                    if (spara0.Y1 != null && spara0.Y1.IsInitialized()) { ho_Y1 = spara0.Y1.Clone(); };
//                    ho_Z1.Dispose();
//                    if (spara0.Z1 != null && spara0.Z1.IsInitialized()) { ho_Z1 = spara0.Z1.Clone(); };
//
//
//                    ho_ImageSubZ1.Dispose();
//                    if (spara0.ImageSubZ1 != null && spara0.ImageSubZ1.IsInitialized()) { ho_ImageSubZ1 = spara0.ImageSubZ1.Clone(); };
//                    ho_ImageZ1ZeroReal.Dispose();
//                    if (spara0.ImageZ1ZeroReal != null && spara0.ImageZ1ZeroReal.IsInitialized())
//                    {
//                        ho_ImageZ1ZeroReal = spara0.ImageZ1ZeroReal.Clone();
//                    };
//
//
//                    ho_Z1PZero.Dispose();
//                    if (spara0.Z1PZero != null && spara0.Z1PZero.IsInitialized()) { ho_Z1PZero = spara0.Z1PZero.Clone(); };
//                    ho_X1PZero.Dispose();
//                    if (spara0.X1PZero != null && spara0.X1PZero.IsInitialized()) { ho_X1PZero = spara0.X1PZero.Clone(); };
//                    ho_Y1PZero.Dispose();
//                    if (spara0.Y1PZero != null && spara0.Y1PZero.IsInitialized()) { ho_Y1PZero = spara0.Y1PZero.Clone(); };
//
//
//
//                    ho_RectPartLzC.Dispose();
//                    if (spara0.RectPartLzC != null && spara0.RectPartLzC.IsInitialized()) { ho_RectPartLzC = spara0.RectPartLzC.Clone(); };
//
//
//                    ho_RectPartLzU.Dispose();
//                    if (spara0.RectPartLzU != null && spara0.RectPartLzU.IsInitialized()) { ho_RectPartLzU = spara0.RectPartLzU.Clone(); };
//
//                    ho_RectPartLzL.Dispose();
//                    if (spara0.RectPartLzL != null && spara0.RectPartLzL.IsInitialized()) { ho_RectPartLzL = spara0.RectPartLzL.Clone(); };
//
//
//                    ho_RectPartLzD.Dispose();
//                    if (spara0.RectPartLzD != null && spara0.RectPartLzD.IsInitialized()) { ho_RectPartLzD = spara0.RectPartLzD.Clone(); };
//
//
//                    ho_RectPartLzR.Dispose();
//                    if (spara0.RectPartLzR != null && spara0.RectPartLzR.IsInitialized()) { ho_RectPartLzR = spara0.RectPartLzR.Clone(); };
//
//
//                    ho_RectangleQgSort.Dispose();
//                    if (spara0.RectangleQgSort != null && spara0.RectangleQgSort.IsInitialized()) { ho_RectangleQgSort = spara0.RectangleQgSort.Clone(); };
//
//
//
//
//                    //工艺参数输入
//                    hv_fDjDiamiter.Dispose();
//                    hv_fDjDiamiter =/* 80.0*/spara1.fDjDiamiter;
//
//                    hv_fJgLzUpOffset.Dispose();
//                    hv_fJgLzUpOffset = /*2*/spara1.fJgLzUpOffset;
//                    hv_fJgDpUpOffset.Dispose();
//                    hv_fJgDpUpOffset = /*1.5*/spara1.fJgDpUpOffset;
//                    hv_iModeJgPPZStepMode.Dispose();
//                    hv_iModeJgPPZStepMode = /*1*/spara1.iModeJgPPZStepMode;
//                    hv_fJgPPZStepFix.Dispose();
//                    hv_fJgPPZStepFix = /*2*/spara1.fJgPPZStepFix;
//                    hv_fJgPPZStepK.Dispose();
//                    hv_fJgPPZStepK = /*0.3*/spara1.fJgPPZStepK;
//                    hv_fJgPPZStepB.Dispose();
//                    hv_fJgPPZStepB = /*1.5*/spara1.fJgPPZStepB;
//
//
//                    hv_iModeJgPPYStepMode.Dispose();
//                    hv_iModeJgPPYStepMode = /*0*/spara1.iModeJgPPYStepMode;
//                    hv_fJgPPYStepFix.Dispose();
//                    hv_fJgPPYStepFix = /*50*/spara1.fJgPPYStepFix;
//                    hv_fJgPPYStepK.Dispose();
//                    hv_fJgPPYStepK = /*0.75*/spara1.fJgPPYStepK;
//
//                    hv_iModeJgPPSort.Dispose();//粒子加工排序 0：从上到下 1：从下到上   2 ：从左到右  3 ：从右到左
//                    hv_iModeJgPPSort = /*0*/spara1.iModeJgPPSort; //该参数内部写死
//
//                    hv_fQgSafeDis.Dispose();
//                    hv_fQgSafeDis =/* 50.0*/spara1.fQgSafeDis;
//
//                    hv_fJgTdZUp.Dispose();
//                    hv_fJgTdZUp = /*20*/spara1.fJgTdZUp;
//
//
//                    //调平坐标系下路径规划-中间
//                    ho_RectPartLzCUnion.Dispose();
//                    HOperatorSet.Union1(ho_RectPartLzC, out ho_RectPartLzCUnion);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_RectPartLzCUnion, ho_ImageSubZ1, 0, out hv_Min,
//                        out hv_Max, out hv_Range);
//
//
//                    //计算当前进给Y
//                    hv_fJgPPYStepCur.Dispose();
//                    hv_fJgPPYStepCur = 20;
//                    if ((int)(new HTuple(hv_iModeJgPPYStepMode.TupleEqual(0))) != 0)
//                    {
//                        hv_fJgPPYStepCur.Dispose();
//                        hv_fJgPPYStepCur = new HTuple(hv_fJgPPYStepFix);
//                    }
//                    else
//                    {
//                        hv_fJgPPYStepCur.Dispose();
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            hv_fJgPPYStepCur = hv_fJgPPYStepK * hv_fDjDiamiter;
//                        }
//                    }
//
//                    //计算像素分辨率
//                    ho_Domain.Dispose();
//                    HOperatorSet.ReduceDomain(ho_Y1, ho_RectPartLzC, out ho_ImageReduced);
//
//                    HOperatorSet.GetDomain(ho_ImageReduced, out ho_Domain);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_Domain, ho_Y1, 0, out hv_Min, out hv_Max, out hv_Range);
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_Domain, out hv_Row1, out hv_Column1, out hv_Row2,
//                        out hv_Column2);
//                    hv_fYResolution.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_fYResolution = hv_Range / (((hv_Row1 - hv_Row2)).TupleAbs()
//                            );
//                    }
//                    hv_iJgPPYStepPixelCur.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_iJgPPYStepPixelCur = ((hv_fJgPPYStepCur / hv_fYResolution)).TupleInt()
//                            ;
//                    }
//
//                    hv_ptsXListZeroRoiC.Dispose();
//                    hv_ptsXListZeroRoiC = new HTuple();
//                    hv_ptsYListZeroRoiC.Dispose();
//                    hv_ptsYListZeroRoiC = new HTuple();
//                    hv_ptsZListZeroRoiC.Dispose();
//                    hv_ptsZListZeroRoiC = new HTuple();
//                    hv_ptsDefListZeroRoiC.Dispose();
//                    hv_ptsDefListZeroRoiC = new HTuple();
//                    hv_ptsRowListRoiC.Dispose();
//                    hv_ptsRowListRoiC = new HTuple();
//                    hv_ptsColListRoiC.Dispose();
//                    hv_ptsColListRoiC = new HTuple();
//                    ho_RegionMxRoiListC.Dispose();
//                    hv_iModeJgPPSort.Dispose();
//                    hv_iModeJgPPSort = 0;
//                    HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListC);
//                    /*  ho_RegionMxRoiList.Dispose();*/ hv_ptsXListZeroRoiC.Dispose(); hv_ptsYListZeroRoiC.Dispose(); hv_ptsZListZeroRoiC.Dispose(); hv_ptsDefListZeroRoiC.Dispose(); hv_ptsRowListRoiC.Dispose(); hv_ptsColListRoiC.Dispose();
//                    cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageSubZ1, ho_ImageZ1ZeroReal, ho_RectPartLzC,
//                        out ho_RegionMxRoiListC, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
//                        hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
//                        out hv_ptsXListZeroRoiC, out hv_ptsYListZeroRoiC, out hv_ptsZListZeroRoiC,
//                        out hv_ptsDefListZeroRoiC, out hv_ptsRowListRoiC, out hv_ptsColListRoiC);
//
//
//
//                    //调平坐标系下路径规划-UP--把气缸区域和飞气缸区域直接合并 一块打磨
//                    ho_RectPartLzUQgUnion.Dispose();
//                    HOperatorSet.Union1(ho_RectPartLzU, out ho_RectPartLzUQgUnion);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_RectPartLzUQgUnion, ho_ImageSubZ1, 0, out hv_Min, out hv_Max, out hv_Range);
//
//                    //计算当前进给Y--共用
//                    //计算像素分辨率--共用
//
//                    hv_ptsXListZeroRoiU.Dispose();
//                    hv_ptsXListZeroRoiU = new HTuple();
//                    hv_ptsYListZeroRoiU.Dispose();
//                    hv_ptsYListZeroRoiU = new HTuple();
//                    hv_ptsZListZeroRoiU.Dispose();
//                    hv_ptsZListZeroRoiU = new HTuple();
//                    hv_ptsDefListZeroRoiU.Dispose();
//                    hv_ptsDefListZeroRoiU = new HTuple();
//
//                    hv_ptsRowListRoiU.Dispose();
//                    hv_ptsRowListRoiU = new HTuple();
//                    hv_ptsColListRoiU.Dispose();
//                    hv_ptsColListRoiU = new HTuple();
//                    ho_RegionMxRoiListU.Dispose();
//                    hv_iModeJgPPSort.Dispose();
//                    hv_iModeJgPPSort = 3;
//                    HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListU);
//                    /*ho_RegionMxRoiList.Dispose();*/ hv_ptsXListZeroRoiU.Dispose(); hv_ptsYListZeroRoiU.Dispose(); hv_ptsZListZeroRoiU.Dispose(); hv_ptsDefListZeroRoiU.Dispose(); hv_ptsRowListRoiU.Dispose(); hv_ptsColListRoiU.Dispose();
//                    cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzU,
//                        out ho_RegionMxRoiListU, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
//                        hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
//                        out hv_ptsXListZeroRoiU, out hv_ptsYListZeroRoiU, out hv_ptsZListZeroRoiU,
//                        out hv_ptsDefListZeroRoiU, out hv_ptsRowListRoiU, out hv_ptsColListRoiU);
//
//
//                    //调平坐标系下路径规划-L--把气缸区域和飞气缸区域直接合并 一块打磨
//
//
//                    ho_RectPartLzLQgUnion.Dispose();
//                    HOperatorSet.Union1(ho_RectPartLzL, out ho_RectPartLzLQgUnion);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_RectPartLzLQgUnion, ho_ImageSubZ1, 0, out hv_Min,
//                        out hv_Max, out hv_Range);
//
//                    //计算当前进给Y--共用
//                    //计算像素分辨率--共用
//
//                    hv_ptsXListZeroRoiL.Dispose();
//                    hv_ptsXListZeroRoiL = new HTuple();
//                    hv_ptsYListZeroRoiL.Dispose();
//                    hv_ptsYListZeroRoiL = new HTuple();
//                    hv_ptsZListZeroRoiL.Dispose();
//                    hv_ptsZListZeroRoiL = new HTuple();
//                    hv_ptsDefListZeroRoiL.Dispose();
//                    hv_ptsDefListZeroRoiL = new HTuple();
//
//                    hv_ptsRowListRoiL.Dispose();
//                    hv_ptsRowListRoiL = new HTuple();
//                    hv_ptsColListRoiL.Dispose();
//                    hv_ptsColListRoiL = new HTuple();
//                    hv_iModeJgPPSort.Dispose();
//                    hv_iModeJgPPSort = 0;
//                    ho_RegionMxRoiListL.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListL);
//                    /*ho_RegionMxRoiList.Dispose(); */hv_ptsXListZeroRoiL.Dispose(); hv_ptsYListZeroRoiL.Dispose(); hv_ptsZListZeroRoiL.Dispose(); hv_ptsDefListZeroRoiL.Dispose(); hv_ptsRowListRoiL.Dispose(); hv_ptsColListRoiL.Dispose();
//                    cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzL,
//                        out ho_RegionMxRoiListL, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
//                        hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
//                        out hv_ptsXListZeroRoiL, out hv_ptsYListZeroRoiL, out hv_ptsZListZeroRoiL,
//                        out hv_ptsDefListZeroRoiL, out hv_ptsRowListRoiL, out hv_ptsColListRoiL);
//
//
//                    ho_RectPartLzDQgUnion.Dispose();
//                    HOperatorSet.Union1(ho_RectPartLzD, out ho_RectPartLzDQgUnion);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_RectPartLzDQgUnion, ho_ImageSubZ1, 0, out hv_Min,
//                        out hv_Max, out hv_Range);
//
//                    //计算当前进给Y--共用
//                    //计算像素分辨率--共用
//
//                    hv_ptsXListZeroRoiD.Dispose();
//                    hv_ptsXListZeroRoiD = new HTuple();
//                    hv_ptsYListZeroRoiD.Dispose();
//                    hv_ptsYListZeroRoiD = new HTuple();
//                    hv_ptsZListZeroRoiD.Dispose();
//                    hv_ptsZListZeroRoiD = new HTuple();
//                    hv_ptsDefListZeroRoiD.Dispose();
//                    hv_ptsDefListZeroRoiD = new HTuple();
//
//                    hv_ptsRowListRoiD.Dispose();
//                    hv_ptsRowListRoiD = new HTuple();
//                    hv_ptsColListRoiD.Dispose();
//                    hv_ptsColListRoiD = new HTuple();
//                    hv_iModeJgPPSort.Dispose();
//                    hv_iModeJgPPSort = 2;
//                    ho_RegionMxRoiListD.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListD);
//                    /*ho_RegionMxRoiList.Dispose();*/ hv_ptsXListZeroRoiD.Dispose(); hv_ptsYListZeroRoiD.Dispose(); hv_ptsZListZeroRoiD.Dispose(); hv_ptsDefListZeroRoiD.Dispose(); hv_ptsRowListRoiD.Dispose(); hv_ptsColListRoiD.Dispose();
//                    cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzD,
//                        out ho_RegionMxRoiListD, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
//                        hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
//                        out hv_ptsXListZeroRoiD, out hv_ptsYListZeroRoiD, out hv_ptsZListZeroRoiD,
//                        out hv_ptsDefListZeroRoiD, out hv_ptsRowListRoiD, out hv_ptsColListRoiD);
//
//
//
//
//                    //调平坐标系下路径规划-R--把气缸区域和飞气缸区域直接合并 一块打磨
//                    ho_RectPartLzRQgUnion.Dispose();
//                    HOperatorSet.Union1(ho_RectPartLzR, out ho_RectPartLzRQgUnion);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_RectPartLzRQgUnion, ho_ImageSubZ1, 0, out hv_Min,
//                        out hv_Max, out hv_Range);
//
//                    //计算当前进给Y--共用
//                    //计算像素分辨率--共用
//
//                    hv_ptsXListZeroRoiR.Dispose();
//                    hv_ptsXListZeroRoiR = new HTuple();
//                    hv_ptsYListZeroRoiR.Dispose();
//                    hv_ptsYListZeroRoiR = new HTuple();
//                    hv_ptsZListZeroRoiR.Dispose();
//                    hv_ptsZListZeroRoiR = new HTuple();
//                    hv_ptsDefListZeroRoiR.Dispose();
//                    hv_ptsDefListZeroRoiR = new HTuple();
//
//                    hv_ptsRowListRoiR.Dispose();
//                    hv_ptsRowListRoiR = new HTuple();
//                    hv_ptsColListRoiR.Dispose();
//                    hv_ptsColListRoiR = new HTuple();
//                    hv_iModeJgPPSort.Dispose();
//                    hv_iModeJgPPSort = 1;
//                    ho_RegionMxRoiListR.Dispose();
//                    HOperatorSet.GenEmptyObj(out ho_RegionMxRoiListR);
//                    /* ho_RegionMxRoiList.Dispose();*/ hv_ptsXListZeroRoiR.Dispose(); hv_ptsYListZeroRoiR.Dispose(); hv_ptsZListZeroRoiR.Dispose(); hv_ptsDefListZeroRoiR.Dispose(); hv_ptsRowListRoiR.Dispose(); hv_ptsColListRoiR.Dispose();
//                    cal_lzgj_image_pp_r1_x(ho_X1PZero, ho_Y1PZero, ho_Z1PZero, ho_ImageZ1ZeroReal, ho_ImageSubZ1, ho_RectPartLzR,
//                        out ho_RegionMxRoiListR, hv_iModeJgPPSort, hv_iJgPPYStepPixelCur, hv_iModeJgPPZStepMode,
//                        hv_fJgPPZStepFix, hv_fJgPPZStepK, hv_fJgPPZStepB, hv_fJgLzUpOffset, hv_fJgDpUpOffset,
//                        out hv_ptsXListZeroRoiR, out hv_ptsYListZeroRoiR, out hv_ptsZListZeroRoiR,
//                        out hv_ptsDefListZeroRoiR, out hv_ptsRowListRoiR, out hv_ptsColListRoiR);
//
//
//
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListC, out ExpTmpOutVar_0
//                        );
//                        ho_RegionMxAllList.Dispose();
//                        ho_RegionMxAllList = ExpTmpOutVar_0;
//
//
//                    }
//
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListU, out ExpTmpOutVar_0
//                        );
//                        ho_RegionMxAllList.Dispose();
//                        ho_RegionMxAllList = ExpTmpOutVar_0;
//
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListL, out ExpTmpOutVar_0
//                        );
//                        ho_RegionMxAllList.Dispose();
//                        ho_RegionMxAllList = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListD, out ExpTmpOutVar_0
//                        );
//                        ho_RegionMxAllList.Dispose();
//                        ho_RegionMxAllList = ExpTmpOutVar_0;
//                    }
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionMxAllList, ho_RegionMxRoiListR, out ExpTmpOutVar_0
//                        );
//                        ho_RegionMxAllList.Dispose();
//                        ho_RegionMxAllList = ExpTmpOutVar_0;
//                    }
//
//
//                    //转换成实际坐标系下的坐标
//
//                    //中间
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseTb, out hv_HomMat3D);
//
//                    hv_ptsXList.Dispose(); hv_ptsYList.Dispose(); hv_ptsZList.Dispose();
//                    HOperatorSet.AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiC, hv_ptsYListZeroRoiC,
//                        hv_ptsZListZeroRoiC, out hv_ptsXList, out hv_ptsYList, out hv_ptsZList);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsXListAll = hv_ptsXListAll.TupleConcat(
//                                    hv_ptsXList);
//                            hv_ptsXListAll.Dispose();
//                            hv_ptsXListAll = ExpTmpLocalVar_ptsXListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListAll = hv_ptsYListAll.TupleConcat(
//                                    hv_ptsYList);
//                            hv_ptsYListAll.Dispose();
//                            hv_ptsYListAll = ExpTmpLocalVar_ptsYListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListAll = hv_ptsZListAll.TupleConcat(
//                                    hv_ptsZList);
//                            hv_ptsZListAll.Dispose();
//                            hv_ptsZListAll = ExpTmpLocalVar_ptsZListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListAll = hv_ptsDefListAll.TupleConcat(
//                                    hv_ptsDefListZeroRoiC);
//                            hv_ptsDefListAll.Dispose();
//                            hv_ptsDefListAll = ExpTmpLocalVar_ptsDefListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListAll = hv_ptsRowListAll.TupleConcat(
//                                    hv_ptsRowListRoiC);
//                            hv_ptsRowListAll.Dispose();
//                            hv_ptsRowListAll = ExpTmpLocalVar_ptsRowListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsColListAll = hv_ptsColListAll.TupleConcat(
//                                    hv_ptsColListRoiC);
//                            hv_ptsColListAll.Dispose();
//                            hv_ptsColListAll = ExpTmpLocalVar_ptsColListAll;
//                        }
//                    }
//
//                    //按中-下-右-上-左顺序加工
//                    //下边
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseTb, out hv_HomMat3D);
//                    hv_ptsXList.Dispose(); hv_ptsYList.Dispose(); hv_ptsZList.Dispose();
//                    HOperatorSet.AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiD, hv_ptsYListZeroRoiD,
//                        hv_ptsZListZeroRoiD, out hv_ptsXList, out hv_ptsYList, out hv_ptsZList);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsXListAll = hv_ptsXListAll.TupleConcat(
//                                    hv_ptsXList);
//                            hv_ptsXListAll.Dispose();
//                            hv_ptsXListAll = ExpTmpLocalVar_ptsXListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListAll = hv_ptsYListAll.TupleConcat(
//                                    hv_ptsYList);
//                            hv_ptsYListAll.Dispose();
//                            hv_ptsYListAll = ExpTmpLocalVar_ptsYListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListAll = hv_ptsZListAll.TupleConcat(
//                                    hv_ptsZList);
//                            hv_ptsZListAll.Dispose();
//                            hv_ptsZListAll = ExpTmpLocalVar_ptsZListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListAll = hv_ptsDefListAll.TupleConcat(
//                                    hv_ptsDefListZeroRoiD);
//                            hv_ptsDefListAll.Dispose();
//                            hv_ptsDefListAll = ExpTmpLocalVar_ptsDefListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListAll = hv_ptsRowListAll.TupleConcat(
//                                    hv_ptsRowListRoiD);
//                            hv_ptsRowListAll.Dispose();
//                            hv_ptsRowListAll = ExpTmpLocalVar_ptsRowListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsColListAll = hv_ptsColListAll.TupleConcat(
//                                    hv_ptsColListRoiD);
//                            hv_ptsColListAll.Dispose();
//                            hv_ptsColListAll = ExpTmpLocalVar_ptsColListAll;
//                        }
//                    }
//
//                    //右边
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseTb, out hv_HomMat3D);
//                    hv_ptsXList.Dispose(); hv_ptsYList.Dispose(); hv_ptsZList.Dispose();
//                    HOperatorSet.AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiR, hv_ptsYListZeroRoiR,
//                        hv_ptsZListZeroRoiR, out hv_ptsXList, out hv_ptsYList, out hv_ptsZList);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsXListAll = hv_ptsXListAll.TupleConcat(
//                                    hv_ptsXList);
//                            hv_ptsXListAll.Dispose();
//                            hv_ptsXListAll = ExpTmpLocalVar_ptsXListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListAll = hv_ptsYListAll.TupleConcat(
//                                    hv_ptsYList);
//                            hv_ptsYListAll.Dispose();
//                            hv_ptsYListAll = ExpTmpLocalVar_ptsYListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListAll = hv_ptsZListAll.TupleConcat(
//                                    hv_ptsZList);
//                            hv_ptsZListAll.Dispose();
//                            hv_ptsZListAll = ExpTmpLocalVar_ptsZListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListAll = hv_ptsDefListAll.TupleConcat(
//                                    hv_ptsDefListZeroRoiR);
//                            hv_ptsDefListAll.Dispose();
//                            hv_ptsDefListAll = ExpTmpLocalVar_ptsDefListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListAll = hv_ptsRowListAll.TupleConcat(
//                                    hv_ptsRowListRoiR);
//                            hv_ptsRowListAll.Dispose();
//                            hv_ptsRowListAll = ExpTmpLocalVar_ptsRowListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsColListAll = hv_ptsColListAll.TupleConcat(
//                                    hv_ptsColListRoiR);
//                            hv_ptsColListAll.Dispose();
//                            hv_ptsColListAll = ExpTmpLocalVar_ptsColListAll;
//                        }
//                    }
//
//
//
//
//                    //上边
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseTb, out hv_HomMat3D);
//                    hv_ptsXList.Dispose(); hv_ptsYList.Dispose(); hv_ptsZList.Dispose();
//                    HOperatorSet.AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiU, hv_ptsYListZeroRoiU,
//                        hv_ptsZListZeroRoiU, out hv_ptsXList, out hv_ptsYList, out hv_ptsZList);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsXListAll = hv_ptsXListAll.TupleConcat(
//                                    hv_ptsXList);
//                            hv_ptsXListAll.Dispose();
//                            hv_ptsXListAll = ExpTmpLocalVar_ptsXListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListAll = hv_ptsYListAll.TupleConcat(
//                                    hv_ptsYList);
//                            hv_ptsYListAll.Dispose();
//                            hv_ptsYListAll = ExpTmpLocalVar_ptsYListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListAll = hv_ptsZListAll.TupleConcat(
//                                    hv_ptsZList);
//                            hv_ptsZListAll.Dispose();
//                            hv_ptsZListAll = ExpTmpLocalVar_ptsZListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListAll = hv_ptsDefListAll.TupleConcat(
//                                    hv_ptsDefListZeroRoiU);
//                            hv_ptsDefListAll.Dispose();
//                            hv_ptsDefListAll = ExpTmpLocalVar_ptsDefListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListAll = hv_ptsRowListAll.TupleConcat(
//                                    hv_ptsRowListRoiU);
//                            hv_ptsRowListAll.Dispose();
//                            hv_ptsRowListAll = ExpTmpLocalVar_ptsRowListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsColListAll = hv_ptsColListAll.TupleConcat(
//                                    hv_ptsColListRoiU);
//                            hv_ptsColListAll.Dispose();
//                            hv_ptsColListAll = ExpTmpLocalVar_ptsColListAll;
//                        }
//                    }
//
//                    //左边
//                    hv_HomMat3D.Dispose();
//                    HOperatorSet.PoseToHomMat3d(hv_PoseTb, out hv_HomMat3D);
//                    hv_ptsXList.Dispose(); hv_ptsYList.Dispose(); hv_ptsZList.Dispose();
//                    HOperatorSet.AffineTransPoint3d(hv_HomMat3D, hv_ptsXListZeroRoiL, hv_ptsYListZeroRoiL,
//                        hv_ptsZListZeroRoiL, out hv_ptsXList, out hv_ptsYList, out hv_ptsZList);
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsXListAll = hv_ptsXListAll.TupleConcat(
//                                    hv_ptsXList);
//                            hv_ptsXListAll.Dispose();
//                            hv_ptsXListAll = ExpTmpLocalVar_ptsXListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListAll = hv_ptsYListAll.TupleConcat(
//                                    hv_ptsYList);
//                            hv_ptsYListAll.Dispose();
//                            hv_ptsYListAll = ExpTmpLocalVar_ptsYListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListAll = hv_ptsZListAll.TupleConcat(
//                                    hv_ptsZList);
//                            hv_ptsZListAll.Dispose();
//                            hv_ptsZListAll = ExpTmpLocalVar_ptsZListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListAll = hv_ptsDefListAll.TupleConcat(
//                                    hv_ptsDefListZeroRoiL);
//                            hv_ptsDefListAll.Dispose();
//                            hv_ptsDefListAll = ExpTmpLocalVar_ptsDefListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListAll = hv_ptsRowListAll.TupleConcat(
//                                    hv_ptsRowListRoiL);
//                            hv_ptsRowListAll.Dispose();
//                            hv_ptsRowListAll = ExpTmpLocalVar_ptsRowListAll;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsColListAll = hv_ptsColListAll.TupleConcat(
//                                    hv_ptsColListRoiL);
//                            hv_ptsColListAll.Dispose();
//                            hv_ptsColListAll = ExpTmpLocalVar_ptsColListAll;
//                        }
//                    }
//
//
//
//
//                    //气缸避位处理
//                    ho_ptsCross.Dispose();
//                    HOperatorSet.GenCrossContourXld(out ho_ptsCross, hv_ptsRowListAll, hv_ptsColListAll, 11, 0);
//
//
//                    //计算像素分辨率
//                    ho_Domain.Dispose();
//                    HOperatorSet.ReduceDomain(ho_X1, ho_RectPartLzC, out ho_ImageReduced);
//                    HOperatorSet.GetDomain(ho_ImageReduced, out ho_Domain);
//                    hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_Domain, ho_X1, 0, out hv_Min, out hv_Max, out hv_Range);
//                    hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_Domain, out hv_Row1, out hv_Column1, out hv_Row2,
//                        out hv_Column2);
//                    hv_fResolution.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_fResolution = hv_Range / (((hv_Column1 - hv_Column2)).TupleAbs());
//                    }
//
//                    hv_fQgSafeDisPixel.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_fQgSafeDisPixel = hv_fQgSafeDis / hv_fResolution;
//                    }
//
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_ptsQgNotSafeListAll.Dispose();
//                        HOperatorSet.TupleGenConst(new HTuple(hv_ptsDefListAll.TupleLength()), "", out hv_ptsQgNotSafeListAll);
//                    }
//
//
//                    hv_iNumQg.Dispose();
//                    HOperatorSet.CountObj(ho_RectangleQgSort, out hv_iNumQg);
//                    hv_iNumPts.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_iNumPts = new HTuple(hv_ptsRowListAll.TupleLength());
//                    }
//
//
//
//                    for (int iPts = 0; iPts < hv_iNumPts.I; iPts++)
//                    {
//
//                        for (int iQg = 0; iQg < hv_iNumQg.I; iQg++)
//                        {
//
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                ho_ObjectSelected.Dispose();
//                                HOperatorSet.SelectObj(ho_RectangleQgSort, out ho_ObjectSelected, iQg + 1);
//                            }
//
//
//
//                            //气缸不存在的时候 直接跳过
//                            hv_Area.Dispose(); hv_Row.Dispose(); hv_Column.Dispose();
//                            HOperatorSet.AreaCenter(ho_ObjectSelected, out hv_Area, out hv_Row, out hv_Column);
//                            if ((int)(new HTuple(hv_Area.TupleLess(100))) != 0)
//                            {
//                                continue;
//                            }
//
//                            hv_Row1.Dispose(); hv_Column1.Dispose(); hv_Row2.Dispose(); hv_Column2.Dispose();
//                            HOperatorSet.SmallestRectangle1(ho_ObjectSelected, out hv_Row1, out hv_Column1, out hv_Row2, out hv_Column2);
//
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                hv_IsInside.Dispose();
//                                HOperatorSet.TestRegionPoint(ho_ObjectSelected, hv_ptsRowListAll.TupleSelect(iPts), hv_ptsColListAll.TupleSelect(iPts), out hv_IsInside);
//                            }
//
//                            if ((int)(new HTuple(hv_IsInside.TupleEqual(1))) != 0)
//                            {
//
//                                if ((int)(new HTuple(((hv_ptsQgNotSafeListAll.TupleSelect(iPts))).TupleEqual(""))) != 0)
//                                {
//                                    if (hv_ptsQgNotSafeListAll == null)
//                                        hv_ptsQgNotSafeListAll = new HTuple();
//                                    hv_ptsQgNotSafeListAll[iPts] = (new HTuple(iQg)).TupleString("d");
//
//                                }
//                                else
//                                {
//                                    hv_str.Dispose();
//                                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                                    {
//                                        hv_str = ((hv_ptsQgNotSafeListAll.TupleSelect(
//                                            iPts)) + new HTuple(",")) + ((new HTuple(iQg)).TupleString("d"));
//                                    }
//                                    if (hv_ptsQgNotSafeListAll == null)
//                                        hv_ptsQgNotSafeListAll = new HTuple();
//                                    hv_ptsQgNotSafeListAll[iPts] = hv_str;
//
//                                }
//
//                                continue;
//
//                            }
//
//
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                hv_DistanceMin.Dispose(); hv_DistanceMax.Dispose();
//                                HOperatorSet.DistancePs(hv_ptsRowListAll.TupleSelect(iPts), hv_ptsColListAll.TupleSelect(
//                                    iPts), hv_Row1, hv_Column1, hv_Row2, hv_Column2, out hv_DistanceMin,
//                                    out hv_DistanceMax);
//                            }
//
//                            if ((int)(new HTuple(hv_DistanceMin.TupleLess(hv_fQgSafeDisPixel))) != 0)
//                            {
//
//                                if ((int)(new HTuple(((hv_ptsQgNotSafeListAll.TupleSelect(iPts))).TupleEqual(
//                                    ""))) != 0)
//                                {
//                                    if (hv_ptsQgNotSafeListAll == null)
//                                        hv_ptsQgNotSafeListAll = new HTuple();
//                                    hv_ptsQgNotSafeListAll[iPts] = (new HTuple(iQg)).TupleString("d");
//                                }
//                                else
//                                {
//                                    hv_str.Dispose();
//                                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                                    {
//                                        hv_str = ((hv_ptsQgNotSafeListAll.TupleSelect(
//                                            iPts)) + new HTuple(",")) + ((new HTuple(iQg)).TupleString("d"));
//                                    }
//                                    if (hv_ptsQgNotSafeListAll == null)
//                                        hv_ptsQgNotSafeListAll = new HTuple();
//                                    hv_ptsQgNotSafeListAll[iPts] = hv_str;
//                                }
//
//
//
//                            }
//
//
//                        }
//
//
//
//                    }
//
//
//
//
//
//                    //****************************************************************************
//                    //点属性定义//1 起点  2 终点  3 中间点  4空跑点
//                    //加入空跑路径点规划
//
//
//                    hv_ptsXListAdv.Dispose();
//                    hv_ptsXListAdv = new HTuple();
//                    hv_ptsYListAdv.Dispose();
//                    hv_ptsYListAdv = new HTuple();
//                    hv_ptsZListAdv.Dispose();
//                    hv_ptsZListAdv = new HTuple();
//                    hv_ptsDefListAdv.Dispose();
//                    hv_ptsDefListAdv = new HTuple();
//                    hv_ptsRowListAdv.Dispose();
//                    hv_ptsRowListAdv = new HTuple();
//                    hv_ptsColListAdv.Dispose();
//                    hv_ptsColListAdv = new HTuple();
//                    hv_ptsQgNotSafeListAdv.Dispose();
//                    hv_ptsQgNotSafeListAdv = new HTuple();
//
//
//
//                    for (int i = 0; i <= (int)((new HTuple(hv_ptsDefListAll.TupleLength())) - 1); i++)
//                    {
//
//                        if ((int)(new HTuple(((hv_ptsDefListAll.TupleSelect(i))).TupleEqual(1))) != 0)
//                        {
//
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsXListAdv = ((hv_ptsXListAdv.TupleConcat(
//                                            hv_ptsXListAll.TupleSelect(i)))).TupleConcat(hv_ptsXListAll.TupleSelect(
//                                                i));
//                                    hv_ptsXListAdv.Dispose();
//                                    hv_ptsXListAdv = ExpTmpLocalVar_ptsXListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsYListAdv = ((hv_ptsYListAdv.TupleConcat(
//                                            hv_ptsYListAll.TupleSelect(i)))).TupleConcat(hv_ptsYListAll.TupleSelect(
//                                                i));
//                                    hv_ptsYListAdv.Dispose();
//                                    hv_ptsYListAdv = ExpTmpLocalVar_ptsYListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsZListAdv = ((hv_ptsZListAdv.TupleConcat(
//                                            (hv_ptsZListAll.TupleSelect(i)) + 20))).TupleConcat(hv_ptsZListAll.TupleSelect(
//                                                i));
//                                    hv_ptsZListAdv.Dispose();
//                                    hv_ptsZListAdv = ExpTmpLocalVar_ptsZListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsDefListAdv = ((hv_ptsDefListAdv.TupleConcat(
//                                            4))).TupleConcat(hv_ptsDefListAll.TupleSelect(i));
//                                    hv_ptsDefListAdv.Dispose();
//                                    hv_ptsDefListAdv = ExpTmpLocalVar_ptsDefListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsRowListAdv = ((hv_ptsRowListAdv.TupleConcat(
//                                            hv_ptsRowListAll.TupleSelect(i)))).TupleConcat(hv_ptsRowListAll.TupleSelect(
//                                                i));
//                                    hv_ptsRowListAdv.Dispose();
//                                    hv_ptsRowListAdv = ExpTmpLocalVar_ptsRowListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsColListAdv = ((hv_ptsColListAdv.TupleConcat(
//                                            hv_ptsColListAll.TupleSelect(i)))).TupleConcat(hv_ptsColListAll.TupleSelect(
//                                                i));
//                                    hv_ptsColListAdv.Dispose();
//                                    hv_ptsColListAdv = ExpTmpLocalVar_ptsColListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsQgNotSafeListAdv = ((hv_ptsQgNotSafeListAdv.TupleConcat(
//                                            hv_ptsQgNotSafeListAll.TupleSelect(i)))).TupleConcat(hv_ptsQgNotSafeListAll.TupleSelect(
//                                                i));
//                                    hv_ptsQgNotSafeListAdv.Dispose();
//                                    hv_ptsQgNotSafeListAdv = ExpTmpLocalVar_ptsQgNotSafeListAdv;
//                                }
//                            }
//
//                        }
//
//                        if ((int)(new HTuple(((hv_ptsDefListAll.TupleSelect(i))).TupleEqual(2))) != 0)
//                        {
//
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsXListAdv = ((hv_ptsXListAdv.TupleConcat(
//                                            hv_ptsXListAll.TupleSelect(i)))).TupleConcat(hv_ptsXListAll.TupleSelect(
//                                                i));
//                                    hv_ptsXListAdv.Dispose();
//                                    hv_ptsXListAdv = ExpTmpLocalVar_ptsXListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsYListAdv = ((hv_ptsYListAdv.TupleConcat(
//                                            hv_ptsYListAll.TupleSelect(i)))).TupleConcat(hv_ptsYListAll.TupleSelect(
//                                                i));
//                                    hv_ptsYListAdv.Dispose();
//                                    hv_ptsYListAdv = ExpTmpLocalVar_ptsYListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsZListAdv = ((hv_ptsZListAdv.TupleConcat(
//                                            hv_ptsZListAll.TupleSelect(i)))).TupleConcat((hv_ptsZListAll.TupleSelect(
//                                                i)) + 20);
//                                    hv_ptsZListAdv.Dispose();
//                                    hv_ptsZListAdv = ExpTmpLocalVar_ptsZListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsDefListAdv = ((hv_ptsDefListAdv.TupleConcat(
//                                            hv_ptsDefListAll.TupleSelect(i)))).TupleConcat(4);
//                                    hv_ptsDefListAdv.Dispose();
//                                    hv_ptsDefListAdv = ExpTmpLocalVar_ptsDefListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsRowListAdv = ((hv_ptsRowListAdv.TupleConcat(
//                                            hv_ptsRowListAll.TupleSelect(i)))).TupleConcat(hv_ptsRowListAll.TupleSelect(
//                                                i));
//                                    hv_ptsRowListAdv.Dispose();
//                                    hv_ptsRowListAdv = ExpTmpLocalVar_ptsRowListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsColListAdv = ((hv_ptsColListAdv.TupleConcat(
//                                            hv_ptsColListAll.TupleSelect(i)))).TupleConcat(hv_ptsColListAll.TupleSelect(
//                                                i));
//                                    hv_ptsColListAdv.Dispose();
//                                    hv_ptsColListAdv = ExpTmpLocalVar_ptsColListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsQgNotSafeListAdv = ((hv_ptsQgNotSafeListAdv.TupleConcat(
//                                            hv_ptsQgNotSafeListAll.TupleSelect(i)))).TupleConcat(hv_ptsQgNotSafeListAll.TupleSelect(
//                                                i));
//                                    hv_ptsQgNotSafeListAdv.Dispose();
//                                    hv_ptsQgNotSafeListAdv = ExpTmpLocalVar_ptsQgNotSafeListAdv;
//                                }
//                            }
//                        }
//
//
//                        if ((int)(new HTuple(((hv_ptsDefListAll.TupleSelect(i))).TupleEqual(3))) != 0)
//                        {
//
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsXListAdv = hv_ptsXListAdv.TupleConcat(
//                                            hv_ptsXListAll.TupleSelect(i));
//                                    hv_ptsXListAdv.Dispose();
//                                    hv_ptsXListAdv = ExpTmpLocalVar_ptsXListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsYListAdv = hv_ptsYListAdv.TupleConcat(
//                                            hv_ptsYListAll.TupleSelect(i));
//                                    hv_ptsYListAdv.Dispose();
//                                    hv_ptsYListAdv = ExpTmpLocalVar_ptsYListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsZListAdv = hv_ptsZListAdv.TupleConcat(
//                                            hv_ptsZListAll.TupleSelect(i));
//                                    hv_ptsZListAdv.Dispose();
//                                    hv_ptsZListAdv = ExpTmpLocalVar_ptsZListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsDefListAdv = hv_ptsDefListAdv.TupleConcat(
//                                            hv_ptsDefListAll.TupleSelect(i));
//                                    hv_ptsDefListAdv.Dispose();
//                                    hv_ptsDefListAdv = ExpTmpLocalVar_ptsDefListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsRowListAdv = hv_ptsRowListAdv.TupleConcat(
//                                            hv_ptsRowListAll.TupleSelect(i));
//                                    hv_ptsRowListAdv.Dispose();
//                                    hv_ptsRowListAdv = ExpTmpLocalVar_ptsRowListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsColListAdv = hv_ptsColListAdv.TupleConcat(
//                                            hv_ptsColListAll.TupleSelect(i));
//                                    hv_ptsColListAdv.Dispose();
//                                    hv_ptsColListAdv = ExpTmpLocalVar_ptsColListAdv;
//                                }
//                            }
//                            using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                            {
//                                {
//                                    HTuple
//                                        ExpTmpLocalVar_ptsQgNotSafeListAdv = hv_ptsQgNotSafeListAdv.TupleConcat(
//                                            hv_ptsQgNotSafeListAll.TupleSelect(i));
//                                    hv_ptsQgNotSafeListAdv.Dispose();
//                                    hv_ptsQgNotSafeListAdv = ExpTmpLocalVar_ptsQgNotSafeListAdv;
//                                }
//                            }
//                        }
//
//                    }
//
//                    #endregion
//
//
//                        //结果数据
//
//                        spara2.bTJG = true;
//
//
//                    spara2.sListPPts.Clear();
//                    for (int i = 0; i < hv_ptsDefListAdv.Length; i++)
//                    {
//                        s_PPts pt = new s_PPts();
//
//                        pt.fX = hv_ptsXListAdv[i].D;
//                        pt.fY = hv_ptsYListAdv[i].D;
//                        pt.fZ = hv_ptsZListAdv[i].D;
//                        pt.iDef = hv_ptsDefListAdv[i].I;
//                        pt.fRow = hv_ptsRowListAdv[i].D;
//                        pt.fCol = hv_ptsColListAdv[i].D;
//                        pt.strQgNotSafe = hv_ptsQgNotSafeListAdv[i].S;
//
//                        spara2.sListPPts.Add(pt.DeepCopy());
//                    }
//
//                    spara2.iNumPts = hv_ptsDefListAdv.Length;
//
//
//                    int iNumRegion = ho_RegionMxAllList.CountObj();
//
//                    spara2.RegionMxAllList.Dispose();
//                    if (ho_RegionMxAllList != null && ho_RegionMxAllList.IsInitialized()) { spara2.RegionMxAllList = ho_RegionMxAllList.Clone(); };
//
//
//                    sError.iCode = 0;
//                    sError.strInfo = "";
//
//                }
//                catch (HalconException ex)
//                {
//                    string str = ex.ToString();
//                    CLogTxt.WriteTxt(str);
//
//                    sError.iCode = -1;
//                    sError.strInfo = "未知异常!";
//                }
//
//
//                break;
//            }
//
//
//        //释放所有临时变量
//
//        HOperatorSet.CountSeconds(out time_end);
//        spara2.time = time_end - time_start;
//        return sError;
//    }
//
//    private void get_plane_ranger_z_out_region_x(HObject ho_Z, out HObject ho_RegionD,
//        out HObject ho_ZSub, out HObject ho_ZZeroReal, HTuple hv_ThZLower, HTuple hv_ThZHiger,
//        HTuple hv_ThZLimit, HTuple hv_MaskWidth, HTuple hv_MaskHeight, HTuple hv_Expand)
//    {
//
//
//
//
//        // Stack for temporary objects 
//        HObject[] OTemp = new HObject[20];
//
//        // Local iconic variables 
//
//        HObject ho_Z1PZeroEx, ho_ImageMean, ho_Domain;
//        HObject ho_RegionFillUp, ho_Region1, ho_Region2, ho_ConnectedRegions;
//        HObject ho_ObjectSelected = null, ho_RegionIntersection = null;
//        HObject ho_ImageMeanZ;
//
//        // Local control variables 
//
//        HTuple hv_Number = new HTuple(), hv_I = new HTuple();
//        HTuple hv_Area = new HTuple(), hv_Row = new HTuple(), hv_Column = new HTuple();
//        HTuple hv_Grayval = new HTuple();
//        // Initialize local and output iconic variables 
//        HOperatorSet.GenEmptyObj(out ho_RegionD);
//        HOperatorSet.GenEmptyObj(out ho_ZSub);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroReal);
//        HOperatorSet.GenEmptyObj(out ho_Z1PZeroEx);
//        HOperatorSet.GenEmptyObj(out ho_ImageMean);
//        HOperatorSet.GenEmptyObj(out ho_Domain);
//        HOperatorSet.GenEmptyObj(out ho_RegionFillUp);
//        HOperatorSet.GenEmptyObj(out ho_Region1);
//        HOperatorSet.GenEmptyObj(out ho_Region2);
//        HOperatorSet.GenEmptyObj(out ho_ConnectedRegions);
//        HOperatorSet.GenEmptyObj(out ho_ObjectSelected);
//        HOperatorSet.GenEmptyObj(out ho_RegionIntersection);
//        HOperatorSet.GenEmptyObj(out ho_ImageMeanZ);
//        try
//        {
//
//            ho_Z1PZeroEx.Dispose();
//            HOperatorSet.ExpandDomainGray(ho_Z, out ho_Z1PZeroEx, hv_Expand);
//            ho_ImageMean.Dispose();
//            HOperatorSet.MeanImage(ho_Z1PZeroEx, out ho_ImageMean, hv_MaskWidth, hv_MaskHeight);
//            ho_ZSub.Dispose();
//            HOperatorSet.SubImage(ho_ImageMean, ho_Z1PZeroEx, out ho_ZSub, 1, 0);
//
//            ho_Domain.Dispose();
//            HOperatorSet.GetDomain(ho_Z, out ho_Domain);
//            ho_RegionFillUp.Dispose();
//            HOperatorSet.FillUp(ho_Domain, out ho_RegionFillUp);
//            {
//                HObject ExpTmpOutVar_0;
//                HOperatorSet.ReduceDomain(ho_ZSub, ho_RegionFillUp, out ExpTmpOutVar_0);
//                ho_ZSub.Dispose();
//                ho_ZSub = ExpTmpOutVar_0;
//            }
//
//
//
//            ho_Region1.Dispose();
//            HOperatorSet.Threshold(ho_ZSub, out ho_Region1, hv_ThZLower, hv_ThZLimit);
//            ho_Region2.Dispose();
//            HOperatorSet.Threshold(ho_ZSub, out ho_Region2, hv_ThZHiger, hv_ThZLimit);
//            ho_ConnectedRegions.Dispose();
//            HOperatorSet.Connection(ho_Region1, out ho_ConnectedRegions);
//
//            ho_RegionD.Dispose();
//            HOperatorSet.GenEmptyObj(out ho_RegionD);
//
//            hv_Number.Dispose();
//            HOperatorSet.CountObj(ho_ConnectedRegions, out hv_Number);
//            HTuple end_val18 = hv_Number;
//            HTuple step_val18 = 1;
//            for (hv_I = 1; hv_I.Continue(end_val18, step_val18); hv_I = hv_I.TupleAdd(step_val18))
//            {
//                ho_ObjectSelected.Dispose();
//                HOperatorSet.SelectObj(ho_ConnectedRegions, out ho_ObjectSelected, hv_I);
//                ho_RegionIntersection.Dispose();
//                HOperatorSet.Intersection(ho_ObjectSelected, ho_Region2, out ho_RegionIntersection
//                );
//                hv_Area.Dispose(); hv_Row.Dispose(); hv_Column.Dispose();
//                HOperatorSet.AreaCenter(ho_RegionIntersection, out hv_Area, out hv_Row, out hv_Column);
//                if ((int)(new HTuple(hv_Area.TupleGreater(0))) != 0)
//                {
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionD, ho_ObjectSelected, out ExpTmpOutVar_0
//                        );
//                        ho_RegionD.Dispose();
//                        ho_RegionD = ExpTmpOutVar_0;
//                    }
//                }
//
//            }
//
//            //额外输出一份真实的高度 Z向上为正
//
//            ho_ImageMeanZ.Dispose();
//            HOperatorSet.MeanImage(ho_Z, out ho_ImageMeanZ, 3, 3);
//            ho_ZZeroReal.Dispose();
//            HOperatorSet.CopyImage(ho_ZSub, out ho_ZZeroReal);
//            hv_Number.Dispose();
//            HOperatorSet.CountObj(ho_RegionD, out hv_Number);
//            HTuple end_val33 = hv_Number;
//            HTuple step_val33 = 1;
//            for (hv_I = 1; hv_I.Continue(end_val33, step_val33); hv_I = hv_I.TupleAdd(step_val33))
//            {
//                ho_ObjectSelected.Dispose();
//                HOperatorSet.SelectObj(ho_ConnectedRegions, out ho_ObjectSelected, hv_I);
//                ho_Domain.Dispose();
//                HOperatorSet.GetDomain(ho_ObjectSelected, out ho_Domain);
//                hv_Row.Dispose(); hv_Column.Dispose();
//                HOperatorSet.GetRegionPoints(ho_Domain, out hv_Row, out hv_Column);
//                hv_Grayval.Dispose();
//                HOperatorSet.GetGrayval(ho_ImageMeanZ, hv_Row, hv_Column, out hv_Grayval);
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    HOperatorSet.SetGrayval(ho_ZZeroReal, hv_Row, hv_Column, -hv_Grayval);
//                }
//
//            }
//
//
//            ho_Z1PZeroEx.Dispose();
//            ho_ImageMean.Dispose();
//            ho_Domain.Dispose();
//            ho_RegionFillUp.Dispose();
//            ho_Region1.Dispose();
//            ho_Region2.Dispose();
//            ho_ConnectedRegions.Dispose();
//            ho_ObjectSelected.Dispose();
//            ho_RegionIntersection.Dispose();
//            ho_ImageMeanZ.Dispose();
//
//            hv_Number.Dispose();
//            hv_I.Dispose();
//            hv_Area.Dispose();
//            hv_Row.Dispose();
//            hv_Column.Dispose();
//            hv_Grayval.Dispose();
//
//            return;
//        }
//        catch (HalconException HDevExpDefaultException)
//        {
//            ho_Z1PZeroEx.Dispose();
//            ho_ImageMean.Dispose();
//            ho_Domain.Dispose();
//            ho_RegionFillUp.Dispose();
//            ho_Region1.Dispose();
//            ho_Region2.Dispose();
//            ho_ConnectedRegions.Dispose();
//            ho_ObjectSelected.Dispose();
//            ho_RegionIntersection.Dispose();
//            ho_ImageMeanZ.Dispose();
//
//            hv_Number.Dispose();
//            hv_I.Dispose();
//            hv_Area.Dispose();
//            hv_Row.Dispose();
//            hv_Column.Dispose();
//            hv_Grayval.Dispose();
//
//            throw HDevExpDefaultException;
//        }
//    }
//
//    private void get_qg_z_out_region_x(HObject ho_Z, HObject ho_RegionQg, out HObject ho_ZSub,
//        out HObject ho_RegionD, out HObject ho_ZZeroReal, HTuple hv_QgHOrg, HTuple hv_ThZOuter,
//        HTuple hv_ThZlimit)
//    {
//
//
//
//
//        // Stack for temporary objects 
//        HObject[] OTemp = new HObject[20];
//
//        // Local iconic variables 
//
//        HObject ho_RegionFillUp, ho_ConnectedRegions;
//        HObject ho_ObjectSelected = null, ho_RegionDilation = null;
//        HObject ho_RegionDifference = null, ho_Domain = null, ho_RegionIntersection = null;
//        HObject ho_RegionOpening = null, ho_RegionErosion = null;
//
//        // Local control variables 
//
//        HTuple hv_Width = new HTuple(), hv_Height = new HTuple();
//        HTuple hv_Number = new HTuple(), hv_I = new HTuple(), hv_MeanRef = new HTuple();
//        HTuple hv_Deviation = new HTuple(), hv_MeanMark = new HTuple();
//        HTuple hv_HQg = new HTuple(), hv_HQgLz = new HTuple();
//        HTuple hv_Rows = new HTuple(), hv_Columns = new HTuple();
//        HTuple hv_Newtuple = new HTuple(), hv_HQg2 = new HTuple();
//        HTuple hv_HQgLz2 = new HTuple(), hv_Newtuple2 = new HTuple();
//        // Initialize local and output iconic variables 
//        HOperatorSet.GenEmptyObj(out ho_ZSub);
//        HOperatorSet.GenEmptyObj(out ho_RegionD);
//        HOperatorSet.GenEmptyObj(out ho_ZZeroReal);
//        HOperatorSet.GenEmptyObj(out ho_RegionFillUp);
//        HOperatorSet.GenEmptyObj(out ho_ConnectedRegions);
//        HOperatorSet.GenEmptyObj(out ho_ObjectSelected);
//        HOperatorSet.GenEmptyObj(out ho_RegionDilation);
//        HOperatorSet.GenEmptyObj(out ho_RegionDifference);
//        HOperatorSet.GenEmptyObj(out ho_Domain);
//        HOperatorSet.GenEmptyObj(out ho_RegionIntersection);
//        HOperatorSet.GenEmptyObj(out ho_RegionOpening);
//        HOperatorSet.GenEmptyObj(out ho_RegionErosion);
//        try
//        {
//
//
//
//            hv_Width.Dispose(); hv_Height.Dispose();
//            HOperatorSet.GetImageSize(ho_Z, out hv_Width, out hv_Height);
//            ho_ZSub.Dispose();
//            HOperatorSet.GenImageConst(out ho_ZSub, "real", hv_Width, hv_Height);
//            ho_ZZeroReal.Dispose();
//            HOperatorSet.GenImageConst(out ho_ZZeroReal, "real", hv_Width, hv_Height);
//            ho_RegionD.Dispose();
//            HOperatorSet.GenEmptyObj(out ho_RegionD);
//
//
//
//            ho_RegionFillUp.Dispose();
//            HOperatorSet.FillUp(ho_RegionQg, out ho_RegionFillUp);
//
//            ho_ConnectedRegions.Dispose();
//            HOperatorSet.Connection(ho_RegionFillUp, out ho_ConnectedRegions);
//            hv_Number.Dispose();
//            HOperatorSet.CountObj(ho_ConnectedRegions, out hv_Number);
//            HTuple end_val14 = hv_Number;
//            HTuple step_val14 = 1;
//            for (hv_I = 1; hv_I.Continue(end_val14, step_val14); hv_I = hv_I.TupleAdd(step_val14))
//            {
//                ho_ObjectSelected.Dispose();
//                HOperatorSet.SelectObj(ho_ConnectedRegions, out ho_ObjectSelected, hv_I);
//
//
//                ho_RegionDilation.Dispose();
//                HOperatorSet.DilationRectangle1(ho_ObjectSelected, out ho_RegionDilation,
//                    71, 71);
//                ho_RegionDifference.Dispose();
//                HOperatorSet.Difference(ho_RegionDilation, ho_ObjectSelected, out ho_RegionDifference
//                );
//
//                ho_Domain.Dispose();
//                HOperatorSet.GetDomain(ho_Z, out ho_Domain);
//                ho_RegionIntersection.Dispose();
//                HOperatorSet.Intersection(ho_RegionDifference, ho_Domain, out ho_RegionIntersection
//                );
//                hv_MeanRef.Dispose(); hv_Deviation.Dispose();
//                HOperatorSet.Intensity(ho_RegionIntersection, ho_Z, out hv_MeanRef, out hv_Deviation);
//
//
//                ho_RegionIntersection.Dispose();
//                HOperatorSet.Intersection(ho_ObjectSelected, ho_Z, out ho_RegionIntersection
//                );
//                ho_RegionFillUp.Dispose();
//                HOperatorSet.FillUp(ho_RegionIntersection, out ho_RegionFillUp);
//                ho_RegionOpening.Dispose();
//                HOperatorSet.OpeningRectangle1(ho_RegionFillUp, out ho_RegionOpening, 5,
//                    5);
//                ho_RegionErosion.Dispose();
//                HOperatorSet.ErosionRectangle1(ho_RegionOpening, out ho_RegionErosion, 21,
//                    21);
//
//                ho_RegionIntersection.Dispose();
//                HOperatorSet.Intersection(ho_RegionErosion, ho_Z, out ho_RegionIntersection
//                );
//                hv_MeanMark.Dispose(); hv_Deviation.Dispose();
//                HOperatorSet.Intensity(ho_RegionIntersection, ho_Z, out hv_MeanMark, out hv_Deviation);
//
//                hv_HQg.Dispose();
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_HQg = ((hv_MeanMark - hv_MeanRef)).TupleAbs()
//                        ;
//                }
//                hv_HQgLz.Dispose();
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_HQgLz = hv_HQg - hv_QgHOrg;
//                }
//
//                hv_Rows.Dispose(); hv_Columns.Dispose();
//                HOperatorSet.GetRegionPoints(ho_ObjectSelected, out hv_Rows, out hv_Columns);
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_Newtuple.Dispose();
//                    HOperatorSet.TupleGenConst(new HTuple(hv_Rows.TupleLength()), hv_HQgLz, out hv_Newtuple);
//                }
//                HOperatorSet.SetGrayval(ho_ZSub, hv_Rows, hv_Columns, hv_Newtuple);
//
//
//                hv_HQg2.Dispose();
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_HQg2 = hv_MeanMark.TupleAbs()
//                        ;
//                }
//                hv_HQgLz2.Dispose();
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_HQgLz2 = hv_HQg2 - hv_QgHOrg;
//                }
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_Newtuple2.Dispose();
//                    HOperatorSet.TupleGenConst(new HTuple(hv_Rows.TupleLength()), hv_HQgLz2,
//                        out hv_Newtuple2);
//                }
//                HOperatorSet.SetGrayval(ho_ZZeroReal, hv_Rows, hv_Columns, hv_Newtuple2);
//
//                if ((int)((new HTuple(hv_HQgLz.TupleGreater(hv_ThZOuter))).TupleAnd(new HTuple(hv_HQgLz.TupleLess(
//                    hv_ThZlimit)))) != 0)
//                {
//
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionD, ho_ObjectSelected, out ExpTmpOutVar_0
//                        );
//                        ho_RegionD.Dispose();
//                        ho_RegionD = ExpTmpOutVar_0;
//                    }
//                }
//
//
//            }
//
//            ho_RegionFillUp.Dispose();
//            ho_ConnectedRegions.Dispose();
//            ho_ObjectSelected.Dispose();
//            ho_RegionDilation.Dispose();
//            ho_RegionDifference.Dispose();
//            ho_Domain.Dispose();
//            ho_RegionIntersection.Dispose();
//            ho_RegionOpening.Dispose();
//            ho_RegionErosion.Dispose();
//
//            hv_Width.Dispose();
//            hv_Height.Dispose();
//            hv_Number.Dispose();
//            hv_I.Dispose();
//            hv_MeanRef.Dispose();
//            hv_Deviation.Dispose();
//            hv_MeanMark.Dispose();
//            hv_HQg.Dispose();
//            hv_HQgLz.Dispose();
//            hv_Rows.Dispose();
//            hv_Columns.Dispose();
//            hv_Newtuple.Dispose();
//            hv_HQg2.Dispose();
//            hv_HQgLz2.Dispose();
//            hv_Newtuple2.Dispose();
//
//            return;
//        }
//        catch (HalconException HDevExpDefaultException)
//        {
//            ho_RegionFillUp.Dispose();
//            ho_ConnectedRegions.Dispose();
//            ho_ObjectSelected.Dispose();
//            ho_RegionDilation.Dispose();
//            ho_RegionDifference.Dispose();
//            ho_Domain.Dispose();
//            ho_RegionIntersection.Dispose();
//            ho_RegionOpening.Dispose();
//            ho_RegionErosion.Dispose();
//
//            hv_Width.Dispose();
//            hv_Height.Dispose();
//            hv_Number.Dispose();
//            hv_I.Dispose();
//            hv_MeanRef.Dispose();
//            hv_Deviation.Dispose();
//            hv_MeanMark.Dispose();
//            hv_HQg.Dispose();
//            hv_HQgLz.Dispose();
//            hv_Rows.Dispose();
//            hv_Columns.Dispose();
//            hv_Newtuple.Dispose();
//            hv_HQg2.Dispose();
//            hv_HQgLz2.Dispose();
//            hv_Newtuple2.Dispose();
//
//            throw HDevExpDefaultException;
//        }
//    }
//
//
//
//    // Local procedures 
//    // Local procedures 
//    private void cal_lzgj_image_pp_r1_x(HObject ho_X, HObject ho_Y, HObject ho_Z, HObject ho_ZReal,
//        HObject ho_ZSub, HObject ho_RectLzs, out HObject ho_RegionMXs, HTuple hv_iModeJgPPSort,
//        HTuple hv_iJgPPYStepPixel, HTuple hv_iModeJgPPZStepMode, HTuple hv_fJgPPZStepFix,
//        HTuple hv_fJgPPZStepK, HTuple hv_fJgPPZStepB, HTuple hv_fJgLzUpOffset, HTuple hv_fJgDpUpOffset,
//        out HTuple hv_ptsXList, out HTuple hv_ptsYList, out HTuple hv_ptsZList, out HTuple hv_ptsDefList,
//        out HTuple hv_ptsRowList, out HTuple hv_ptsColList)
//    {
//
//
//
//
//        // Stack for temporary objects 
//        HObject[] OTemp = new HObject[20];
//
//        // Local iconic variables 
//
//        HObject ho_SortedRegions = null, ho_LzSelected = null;
//        HObject ho_Partitioned = null, ho_RegionMxList = null, ho_ObjectSelected = null;
//        HObject ho_Domain = null, ho_RegionIntersection = null, ho_RegionMx = null;
//
//        // Local control variables 
//
//        HTuple hv_NumLz = new HTuple(), hv_iNumLz = new HTuple();
//        HTuple hv_NumPart = new HTuple(), hv_ptsXListZeroS = new HTuple();
//        HTuple hv_ptsYListZeroS = new HTuple(), hv_ptsZListZeroS = new HTuple();
//        HTuple hv_ptsDefListZeroS = new HTuple(), hv_ptsRowListS = new HTuple();
//        HTuple hv_ptsColListS = new HTuple(), hv_bOdd = new HTuple();
//        HTuple hv_iPart = new HTuple(), hv_MinX = new HTuple();
//        HTuple hv_MaxX = new HTuple(), hv_Range = new HTuple();
//        HTuple hv_MeanY = new HTuple(), hv_Deviation = new HTuple();
//        HTuple hv_Row13 = new HTuple(), hv_Column13 = new HTuple();
//        HTuple hv_Row23 = new HTuple(), hv_Column23 = new HTuple();
//        HTuple hv_ValX1 = new HTuple(), hv_ValX2 = new HTuple();
//        HTuple hv_ValY = new HTuple(), hv_RowCenter = new HTuple();
//        HTuple hv_ptsXListZeroM = new HTuple(), hv_ptsYListZeroM = new HTuple();
//        HTuple hv_ptsZListZeroM = new HTuple(), hv_ptsDefListZeroM = new HTuple();
//        HTuple hv_ptsRowListZeroM = new HTuple(), hv_ptsColListZeroM = new HTuple();
//        HTuple hv_Min = new HTuple(), hv_Max = new HTuple(), hv_Min2 = new HTuple();
//        HTuple hv_Max2 = new HTuple(), hv_Range2 = new HTuple();
//        HTuple hv_DmZ = new HTuple(), hv_LzHeight = new HTuple();
//        HTuple hv_MxHeight = new HTuple(), hv_fMxZCur = new HTuple();
//        HTuple hv_iLayer = new HTuple(), hv_bLast = new HTuple();
//        HTuple hv_fJgPPZStepCur = new HTuple(), hv_Newtuple = new HTuple();
//        HTuple hv_ddd = new HTuple(), hv_ddd2 = new HTuple();
//        // Initialize local and output iconic variables 
//        HOperatorSet.GenEmptyObj(out ho_RegionMXs);
//        HOperatorSet.GenEmptyObj(out ho_SortedRegions);
//        HOperatorSet.GenEmptyObj(out ho_LzSelected);
//        HOperatorSet.GenEmptyObj(out ho_Partitioned);
//        HOperatorSet.GenEmptyObj(out ho_RegionMxList);
//        HOperatorSet.GenEmptyObj(out ho_ObjectSelected);
//        HOperatorSet.GenEmptyObj(out ho_Domain);
//        HOperatorSet.GenEmptyObj(out ho_RegionIntersection);
//        HOperatorSet.GenEmptyObj(out ho_RegionMx);
//        hv_ptsXList = new HTuple();
//        hv_ptsYList = new HTuple();
//        hv_ptsZList = new HTuple();
//        hv_ptsDefList = new HTuple();
//        hv_ptsRowList = new HTuple();
//        hv_ptsColList = new HTuple();
//        try
//        {
//
//            hv_ptsXList.Dispose();
//            hv_ptsXList = new HTuple();
//            hv_ptsYList.Dispose();
//            hv_ptsYList = new HTuple();
//            hv_ptsZList.Dispose();
//            hv_ptsZList = new HTuple();
//            hv_ptsDefList.Dispose();
//            hv_ptsDefList = new HTuple();
//
//            hv_ptsRowList.Dispose();
//            hv_ptsRowList = new HTuple();
//            hv_ptsColList.Dispose();
//            hv_ptsColList = new HTuple();
//
//            ho_RegionMXs.Dispose();
//            HOperatorSet.GenEmptyObj(out ho_RegionMXs);
//
//            if ((int)(new HTuple(hv_iModeJgPPSort.TupleEqual(0))) != 0)
//            {
//
//                ho_SortedRegions.Dispose();
//                HOperatorSet.SortRegion(ho_RectLzs, out ho_SortedRegions, "first_point",
//                    "true", "row");
//            }
//            else if ((int)(new HTuple(hv_iModeJgPPSort.TupleEqual(1))) != 0)
//            {
//                ho_SortedRegions.Dispose();
//                HOperatorSet.SortRegion(ho_RectLzs, out ho_SortedRegions, "first_point",
//                    "false", "row");
//            }
//            else if ((int)(new HTuple(hv_iModeJgPPSort.TupleEqual(2))) != 0)
//            {
//                ho_SortedRegions.Dispose();
//                HOperatorSet.SortRegion(ho_RectLzs, out ho_SortedRegions, "first_point",
//                    "true", "column");
//            }
//            else
//            {
//                ho_SortedRegions.Dispose();
//                HOperatorSet.SortRegion(ho_RectLzs, out ho_SortedRegions, "first_point",
//                    "false", "column");
//            }
//
//            hv_NumLz.Dispose();
//            HOperatorSet.CountObj(ho_SortedRegions, out hv_NumLz);
//            HTuple end_val23 = hv_NumLz - 1;
//            HTuple step_val23 = 1;
//            for (hv_iNumLz = 0; hv_iNumLz.Continue(end_val23, step_val23); hv_iNumLz = hv_iNumLz.TupleAdd(step_val23))
//            {
//                //Y方向切块 根据设置的mm进给值计算出切割像素值
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    ho_LzSelected.Dispose();
//                    HOperatorSet.SelectObj(ho_SortedRegions, out ho_LzSelected, hv_iNumLz + 1);
//                }
//                ho_Partitioned.Dispose();
//                HOperatorSet.PartitionRectangle(ho_LzSelected, out ho_Partitioned, 3000,
//                    hv_iJgPPYStepPixel);
//
//                hv_NumPart.Dispose();
//                HOperatorSet.CountObj(ho_Partitioned, out hv_NumPart);
//
//
//                ho_RegionMxList.Dispose();
//                HOperatorSet.GenEmptyObj(out ho_RegionMxList);
//                hv_ptsXListZeroS.Dispose();
//                hv_ptsXListZeroS = new HTuple();
//                hv_ptsYListZeroS.Dispose();
//                hv_ptsYListZeroS = new HTuple();
//                hv_ptsZListZeroS.Dispose();
//                hv_ptsZListZeroS = new HTuple();
//                hv_ptsDefListZeroS.Dispose();
//                hv_ptsDefListZeroS = new HTuple();
//
//                hv_ptsRowListS.Dispose();
//                hv_ptsRowListS = new HTuple();
//                hv_ptsColListS.Dispose();
//                hv_ptsColListS = new HTuple();
//
//                hv_bOdd.Dispose();
//                hv_bOdd = 0;
//
//                HTuple end_val42 = hv_NumPart - 1;
//                HTuple step_val42 = 1;
//                for (hv_iPart = 0; hv_iPart.Continue(end_val42, step_val42); hv_iPart = hv_iPart.TupleAdd(step_val42))
//                {
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        ho_ObjectSelected.Dispose();
//                        HOperatorSet.SelectObj(ho_Partitioned, out ho_ObjectSelected, hv_iPart + 1);
//                    }
//
//                    ho_Domain.Dispose();
//                    HOperatorSet.GetDomain(ho_Z, out ho_Domain);
//                    ho_RegionIntersection.Dispose();
//                    HOperatorSet.Intersection(ho_ObjectSelected, ho_Domain, out ho_RegionIntersection
//                    );
//
//                    hv_MinX.Dispose(); hv_MaxX.Dispose(); hv_Range.Dispose();
//                    HOperatorSet.MinMaxGray(ho_RegionIntersection, ho_X, 0, out hv_MinX, out hv_MaxX,
//                        out hv_Range);
//                    hv_MeanY.Dispose(); hv_Deviation.Dispose();
//                    HOperatorSet.Intensity(ho_RegionIntersection, ho_Y, out hv_MeanY, out hv_Deviation);
//                    hv_Row13.Dispose(); hv_Column13.Dispose(); hv_Row23.Dispose(); hv_Column23.Dispose();
//                    HOperatorSet.SmallestRectangle1(ho_ObjectSelected, out hv_Row13, out hv_Column13,
//                        out hv_Row23, out hv_Column23);
//                    ho_RegionMx.Dispose();
//                    HOperatorSet.GenRectangle1(out ho_RegionMx, hv_Row13, hv_Column13, hv_Row23,
//                        hv_Column23);
//
//                    {
//                        HObject ExpTmpOutVar_0;
//                        HOperatorSet.ConcatObj(ho_RegionMxList, ho_RegionMx, out ExpTmpOutVar_0
//                        );
//                        ho_RegionMxList.Dispose();
//                        ho_RegionMxList = ExpTmpOutVar_0;
//                    }
//
//
//                    hv_ValX1.Dispose();
//                    hv_ValX1 = new HTuple(hv_MinX);
//                    hv_ValX2.Dispose();
//                    hv_ValX2 = new HTuple(hv_MaxX);
//                    hv_ValY.Dispose();
//                    hv_ValY = new HTuple(hv_MeanY);
//
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListZeroS = hv_ptsYListZeroS.TupleConcat(
//                                    hv_ValY);
//                            hv_ptsYListZeroS.Dispose();
//                            hv_ptsYListZeroS = ExpTmpLocalVar_ptsYListZeroS;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListZeroS = hv_ptsZListZeroS.TupleConcat(
//                                    0);
//                            hv_ptsZListZeroS.Dispose();
//                            hv_ptsZListZeroS = ExpTmpLocalVar_ptsZListZeroS;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListZeroS = hv_ptsYListZeroS.TupleConcat(
//                                    hv_ValY);
//                            hv_ptsYListZeroS.Dispose();
//                            hv_ptsYListZeroS = ExpTmpLocalVar_ptsYListZeroS;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListZeroS = hv_ptsZListZeroS.TupleConcat(
//                                    0);
//                            hv_ptsZListZeroS.Dispose();
//                            hv_ptsZListZeroS = ExpTmpLocalVar_ptsZListZeroS;
//                        }
//                    }
//
//                    hv_RowCenter.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_RowCenter = (hv_Row13 / 2) + (hv_Row23 / 2);
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListS = hv_ptsRowListS.TupleConcat(
//                                    hv_RowCenter);
//                            hv_ptsRowListS.Dispose();
//                            hv_ptsRowListS = ExpTmpLocalVar_ptsRowListS;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListS = hv_ptsRowListS.TupleConcat(
//                                    hv_RowCenter);
//                            hv_ptsRowListS.Dispose();
//                            hv_ptsRowListS = ExpTmpLocalVar_ptsRowListS;
//                        }
//                    }
//
//                    hv_bOdd.Dispose();
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_bOdd = hv_iPart % 2;
//                    }
//                    if ((int)(new HTuple(hv_bOdd.TupleEqual(0))) != 0)
//                    {
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(
//                                        hv_MinX);
//                                hv_ptsXListZeroS.Dispose();
//                                hv_ptsXListZeroS = ExpTmpLocalVar_ptsXListZeroS;
//                            }
//                        }
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(
//                                        hv_MaxX);
//                                hv_ptsXListZeroS.Dispose();
//                                hv_ptsXListZeroS = ExpTmpLocalVar_ptsXListZeroS;
//                            }
//                        }
//
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsColListS = hv_ptsColListS.TupleConcat(
//                                        hv_Column13);
//                                hv_ptsColListS.Dispose();
//                                hv_ptsColListS = ExpTmpLocalVar_ptsColListS;
//                            }
//                        }
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsColListS = hv_ptsColListS.TupleConcat(
//                                        hv_Column23);
//                                hv_ptsColListS.Dispose();
//                                hv_ptsColListS = ExpTmpLocalVar_ptsColListS;
//                            }
//                        }
//
//                    }
//                    else
//                    {
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(
//                                        hv_MaxX);
//                                hv_ptsXListZeroS.Dispose();
//                                hv_ptsXListZeroS = ExpTmpLocalVar_ptsXListZeroS;
//                            }
//                        }
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsXListZeroS = hv_ptsXListZeroS.TupleConcat(
//                                        hv_MinX);
//                                hv_ptsXListZeroS.Dispose();
//                                hv_ptsXListZeroS = ExpTmpLocalVar_ptsXListZeroS;
//                            }
//                        }
//
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsColListS = hv_ptsColListS.TupleConcat(
//                                        hv_Column23);
//                                hv_ptsColListS.Dispose();
//                                hv_ptsColListS = ExpTmpLocalVar_ptsColListS;
//                            }
//                        }
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            {
//                                HTuple
//                                    ExpTmpLocalVar_ptsColListS = hv_ptsColListS.TupleConcat(
//                                        hv_Column13);
//                                hv_ptsColListS.Dispose();
//                                hv_ptsColListS = ExpTmpLocalVar_ptsColListS;
//                            }
//                        }
//
//                    }
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListZeroS = hv_ptsDefListZeroS.TupleConcat(
//                                    3);
//                            hv_ptsDefListZeroS.Dispose();
//                            hv_ptsDefListZeroS = ExpTmpLocalVar_ptsDefListZeroS;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListZeroS = hv_ptsDefListZeroS.TupleConcat(
//                                    3);
//                            hv_ptsDefListZeroS.Dispose();
//                            hv_ptsDefListZeroS = ExpTmpLocalVar_ptsDefListZeroS;
//                        }
//                    }
//
//
//                }
//
//                //包含Z深度方向多层路径规划
//                hv_ptsXListZeroM.Dispose();
//                hv_ptsXListZeroM = new HTuple();
//                hv_ptsYListZeroM.Dispose();
//                hv_ptsYListZeroM = new HTuple();
//                hv_ptsZListZeroM.Dispose();
//                hv_ptsZListZeroM = new HTuple();
//                hv_ptsDefListZeroM.Dispose();
//                hv_ptsDefListZeroM = new HTuple();
//
//                hv_ptsRowListZeroM.Dispose();
//                hv_ptsRowListZeroM = new HTuple();
//                hv_ptsColListZeroM.Dispose();
//                hv_ptsColListZeroM = new HTuple();
//
//                //粒子绝对高度
//                hv_Min.Dispose(); hv_Max.Dispose(); hv_Range.Dispose();
//                HOperatorSet.MinMaxGray(ho_LzSelected, ho_ZReal, 0, out hv_Min, out hv_Max,
//                    out hv_Range);
//                //粒子相对高度
//                hv_Min2.Dispose(); hv_Max2.Dispose(); hv_Range2.Dispose();
//                HOperatorSet.MinMaxGray(ho_LzSelected, ho_ZSub, 0, out hv_Min2, out hv_Max2,
//                    out hv_Range2);
//
//                //粒子底部相对于零平面的高度
//                hv_DmZ.Dispose();
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_DmZ = hv_Max - hv_Max2;
//                }
//
//                hv_LzHeight.Dispose();
//                hv_LzHeight = new HTuple(hv_Max);
//                hv_MxHeight.Dispose();
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    hv_MxHeight = ((hv_LzHeight + hv_fJgLzUpOffset) - hv_fJgDpUpOffset) - hv_DmZ;
//                }
//
//                hv_fMxZCur.Dispose();
//                hv_fMxZCur = new HTuple(hv_LzHeight);
//                for (hv_iLayer = 0; (int)hv_iLayer <= 100; hv_iLayer = (int)hv_iLayer + 1)
//                {
//
//                    hv_bLast.Dispose();
//                    hv_bLast = 0;
//
//                    //计算当前进给Z
//                    hv_fJgPPZStepCur.Dispose();
//                    hv_fJgPPZStepCur = 1.0;
//                    if ((int)(new HTuple(hv_iModeJgPPZStepMode.TupleEqual(0))) != 0)
//                    {
//                        hv_fJgPPZStepCur.Dispose();
//                        hv_fJgPPZStepCur = new HTuple(hv_fJgPPZStepFix);
//                    }
//                    else
//                    {
//                        hv_fJgPPZStepCur.Dispose();
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            hv_fJgPPZStepCur = (hv_fJgPPZStepK * hv_fMxZCur) + hv_fJgPPZStepB;
//                        }
//                    }
//
//
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_fMxZCur = hv_fMxZCur - hv_fJgPPZStepCur;
//                            hv_fMxZCur.Dispose();
//                            hv_fMxZCur = ExpTmpLocalVar_fMxZCur;
//                        }
//                    }
//                    if ((int)(new HTuple(hv_fMxZCur.TupleLess(hv_fJgDpUpOffset + hv_DmZ))) != 0)
//                    {
//                        hv_fMxZCur.Dispose();
//                        using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                        {
//                            hv_fMxZCur = hv_fJgDpUpOffset + hv_DmZ;
//                        }
//                        hv_bLast.Dispose();
//                        hv_bLast = 1;
//                    }
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsXListZeroM = hv_ptsXListZeroM.TupleConcat(
//                                    hv_ptsXListZeroS);
//                            hv_ptsXListZeroM.Dispose();
//                            hv_ptsXListZeroM = ExpTmpLocalVar_ptsXListZeroM;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsYListZeroM = hv_ptsYListZeroM.TupleConcat(
//                                    hv_ptsYListZeroS);
//                            hv_ptsYListZeroM.Dispose();
//                            hv_ptsYListZeroM = ExpTmpLocalVar_ptsYListZeroM;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        hv_Newtuple.Dispose();
//                        HOperatorSet.TupleGenConst(new HTuple(hv_ptsZListZeroS.TupleLength()),
//                            hv_fMxZCur * -1.0, out hv_Newtuple);
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsZListZeroM = hv_ptsZListZeroM.TupleConcat(
//                                    hv_Newtuple);
//                            hv_ptsZListZeroM.Dispose();
//                            hv_ptsZListZeroM = ExpTmpLocalVar_ptsZListZeroM;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsDefListZeroM = hv_ptsDefListZeroM.TupleConcat(
//                                    hv_ptsDefListZeroS);
//                            hv_ptsDefListZeroM.Dispose();
//                            hv_ptsDefListZeroM = ExpTmpLocalVar_ptsDefListZeroM;
//                        }
//                    }
//
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsRowListZeroM = hv_ptsRowListZeroM.TupleConcat(
//                                    hv_ptsRowListS);
//                            hv_ptsRowListZeroM.Dispose();
//                            hv_ptsRowListZeroM = ExpTmpLocalVar_ptsRowListZeroM;
//                        }
//                    }
//                    using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                    {
//                        {
//                            HTuple
//                                ExpTmpLocalVar_ptsColListZeroM = hv_ptsColListZeroM.TupleConcat(
//                                    hv_ptsColListS);
//                            hv_ptsColListZeroM.Dispose();
//                            hv_ptsColListZeroM = ExpTmpLocalVar_ptsColListZeroM;
//                        }
//                    }
//
//
//                    if ((int)(hv_bLast) != 0)
//                    {
//                        break;
//                    }
//
//                }
//
//                if (hv_ptsDefListZeroM == null)
//                    hv_ptsDefListZeroM = new HTuple();
//                hv_ptsDefListZeroM[0] = 1;
//                if (hv_ptsDefListZeroM == null)
//                    hv_ptsDefListZeroM = new HTuple();
//                hv_ptsDefListZeroM[(new HTuple(hv_ptsDefListZeroM.TupleLength())) - 1] = 2;
//
//
//
//                //添加到区域
//
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    {
//                        HTuple
//                            ExpTmpLocalVar_ptsXList = hv_ptsXList.TupleConcat(
//                                hv_ptsXListZeroM);
//                        hv_ptsXList.Dispose();
//                        hv_ptsXList = ExpTmpLocalVar_ptsXList;
//                    }
//                }
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    {
//                        HTuple
//                            ExpTmpLocalVar_ptsYList = hv_ptsYList.TupleConcat(
//                                hv_ptsYListZeroM);
//                        hv_ptsYList.Dispose();
//                        hv_ptsYList = ExpTmpLocalVar_ptsYList;
//                    }
//                }
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    {
//                        HTuple
//                            ExpTmpLocalVar_ptsZList = hv_ptsZList.TupleConcat(
//                                hv_ptsZListZeroM);
//                        hv_ptsZList.Dispose();
//                        hv_ptsZList = ExpTmpLocalVar_ptsZList;
//                    }
//                }
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    {
//                        HTuple
//                            ExpTmpLocalVar_ptsDefList = hv_ptsDefList.TupleConcat(
//                                hv_ptsDefListZeroM);
//                        hv_ptsDefList.Dispose();
//                        hv_ptsDefList = ExpTmpLocalVar_ptsDefList;
//                    }
//                }
//
//
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    {
//                        HTuple
//                            ExpTmpLocalVar_ptsRowList = hv_ptsRowList.TupleConcat(
//                                hv_ptsRowListZeroM);
//                        hv_ptsRowList.Dispose();
//                        hv_ptsRowList = ExpTmpLocalVar_ptsRowList;
//                    }
//                }
//                using (HDevDisposeHelper dh = new HDevDisposeHelper())
//                {
//                    {
//                        HTuple
//                            ExpTmpLocalVar_ptsColList = hv_ptsColList.TupleConcat(
//                                hv_ptsColListZeroM);
//                        hv_ptsColList.Dispose();
//                        hv_ptsColList = ExpTmpLocalVar_ptsColList;
//                    }
//                }
//
//                {
//                    HObject ExpTmpOutVar_0;
//                    HOperatorSet.ConcatObj(ho_RegionMXs, ho_RegionMxList, out ExpTmpOutVar_0);
//                    ho_RegionMXs.Dispose();
//                    ho_RegionMXs = ExpTmpOutVar_0;
//                }
//
//                hv_ddd.Dispose();
//                hv_ddd = 0;
//
//            }
//
//
//            hv_ddd2.Dispose();
//            hv_ddd2 = 0;
//
//            ho_SortedRegions.Dispose();
//            ho_LzSelected.Dispose();
//            ho_Partitioned.Dispose();
//            ho_RegionMxList.Dispose();
//            ho_ObjectSelected.Dispose();
//            ho_Domain.Dispose();
//            ho_RegionIntersection.Dispose();
//            ho_RegionMx.Dispose();
//
//            hv_NumLz.Dispose();
//            hv_iNumLz.Dispose();
//            hv_NumPart.Dispose();
//            hv_ptsXListZeroS.Dispose();
//            hv_ptsYListZeroS.Dispose();
//            hv_ptsZListZeroS.Dispose();
//            hv_ptsDefListZeroS.Dispose();
//            hv_ptsRowListS.Dispose();
//            hv_ptsColListS.Dispose();
//            hv_bOdd.Dispose();
//            hv_iPart.Dispose();
//            hv_MinX.Dispose();
//            hv_MaxX.Dispose();
//            hv_Range.Dispose();
//            hv_MeanY.Dispose();
//            hv_Deviation.Dispose();
//            hv_Row13.Dispose();
//            hv_Column13.Dispose();
//            hv_Row23.Dispose();
//            hv_Column23.Dispose();
//            hv_ValX1.Dispose();
//            hv_ValX2.Dispose();
//            hv_ValY.Dispose();
//            hv_RowCenter.Dispose();
//            hv_ptsXListZeroM.Dispose();
//            hv_ptsYListZeroM.Dispose();
//            hv_ptsZListZeroM.Dispose();
//            hv_ptsDefListZeroM.Dispose();
//            hv_ptsRowListZeroM.Dispose();
//            hv_ptsColListZeroM.Dispose();
//            hv_Min.Dispose();
//            hv_Max.Dispose();
//            hv_Min2.Dispose();
//            hv_Max2.Dispose();
//            hv_Range2.Dispose();
//            hv_DmZ.Dispose();
//            hv_LzHeight.Dispose();
//            hv_MxHeight.Dispose();
//            hv_fMxZCur.Dispose();
//            hv_iLayer.Dispose();
//            hv_bLast.Dispose();
//            hv_fJgPPZStepCur.Dispose();
//            hv_Newtuple.Dispose();
//            hv_ddd.Dispose();
//            hv_ddd2.Dispose();
//
//            return;
//        }
//        catch (HalconException HDevExpDefaultException)
//        {
//            ho_SortedRegions.Dispose();
//            ho_LzSelected.Dispose();
//            ho_Partitioned.Dispose();
//            ho_RegionMxList.Dispose();
//            ho_ObjectSelected.Dispose();
//            ho_Domain.Dispose();
//            ho_RegionIntersection.Dispose();
//            ho_RegionMx.Dispose();
//
//            hv_NumLz.Dispose();
//            hv_iNumLz.Dispose();
//            hv_NumPart.Dispose();
//            hv_ptsXListZeroS.Dispose();
//            hv_ptsYListZeroS.Dispose();
//            hv_ptsZListZeroS.Dispose();
//            hv_ptsDefListZeroS.Dispose();
//            hv_ptsRowListS.Dispose();
//            hv_ptsColListS.Dispose();
//            hv_bOdd.Dispose();
//            hv_iPart.Dispose();
//            hv_MinX.Dispose();
//            hv_MaxX.Dispose();
//            hv_Range.Dispose();
//            hv_MeanY.Dispose();
//            hv_Deviation.Dispose();
//            hv_Row13.Dispose();
//            hv_Column13.Dispose();
//            hv_Row23.Dispose();
//            hv_Column23.Dispose();
//            hv_ValX1.Dispose();
//            hv_ValX2.Dispose();
//            hv_ValY.Dispose();
//            hv_RowCenter.Dispose();
//            hv_ptsXListZeroM.Dispose();
//            hv_ptsYListZeroM.Dispose();
//            hv_ptsZListZeroM.Dispose();
//            hv_ptsDefListZeroM.Dispose();
//            hv_ptsRowListZeroM.Dispose();
//            hv_ptsColListZeroM.Dispose();
//            hv_Min.Dispose();
//            hv_Max.Dispose();
//            hv_Min2.Dispose();
//            hv_Max2.Dispose();
//            hv_Range2.Dispose();
//            hv_DmZ.Dispose();
//            hv_LzHeight.Dispose();
//            hv_MxHeight.Dispose();
//            hv_fMxZCur.Dispose();
//            hv_iLayer.Dispose();
//            hv_bLast.Dispose();
//            hv_fJgPPZStepCur.Dispose();
//            hv_Newtuple.Dispose();
//            hv_ddd.Dispose();
//            hv_ddd2.Dispose();
//
//            throw HDevExpDefaultException;
//        }
//    }
//
//
//}
//}
//
//
//
//#endregion
//
//
//#endregion
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



