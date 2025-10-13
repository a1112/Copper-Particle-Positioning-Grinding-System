#pragma once

#include <windows.h> // ����Windows API�����ͷ�ļ�
#include "DataX.h"


class CHVisionAdvX
{

public:
    CHVisionAdvX();
    virtual ~CHVisionAdvX();


  
    bool is_directory_exists(const std::string& path);

    bool is_file_exists(const std::string& path);

    int ReadImage3DX(s_Image3dS& imgTable,
        std::string sFullPathNameRemoveSuffix,  //ͼ��ȫ·��ȥ����׺������
        std::string strGraySuffix = "_IMG_Texture_8Bit",      //�Ҷ�ͼ��׺
        std::string strPointCloudSuffix = "_IMG_PointCloud_",  //���ƺ�׺
        std::string strNormalSuffix = "_IMG_NormalMap_"     //���ߺ�׺
    );
    

    int  WriteImage3DX(s_Image3dS imgTable, std::string szFolderPath, std::string sNameRemoveSuffix);

    void gen_arrow_contour_xld(HObject* ho_Arrow, HTuple hv_Row1, HTuple hv_Column1, HTuple hv_Row2, HTuple hv_Column2, HTuple hv_HeadLength, HTuple hv_HeadWidth);







};

