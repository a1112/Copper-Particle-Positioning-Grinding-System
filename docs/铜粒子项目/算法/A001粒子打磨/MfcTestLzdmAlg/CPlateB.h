#pragma once

#include "DataX.h"

class CPlateB
{

   
public:
    CPlateB();
    virtual ~CPlateB();

    //缺陷检测+自动分区
    s_Rtnf OnDetect(s_Image3dS Image3d, s_DefectPlateBPara spara1, s_DefectPlateBRtsPara& spara2);

     //执行粒子路径规划
    s_Rtnf OnLzPP(s_JggyPara spara1, s_DefectPlateBRtsPara spara0, s_LzppRtsPara& spara2);

private:
    void get_plane_ranger_z_out_region_x(HObject ho_Z, HObject* ho_RegionD, HObject* ho_ZSub,
        HObject* ho_ZZeroReal, HTuple hv_ThZLower, HTuple hv_ThZHiger, HTuple hv_ThZLimit,
        HTuple hv_MaskWidth, HTuple hv_MaskHeight, HTuple hv_Expand);

    void get_qg_z_out_region_x(HObject ho_Z, HObject ho_RegionQg, HObject* ho_ZSub,
        HObject* ho_RegionD, HObject* ho_ZZeroReal, HTuple hv_QgHOrg, HTuple hv_ThZOuter,
        HTuple hv_ThZlimit);

    void CPlateB::cal_lzgj_image_pp_r1_x(HObject ho_X, HObject ho_Y, HObject ho_Z, HObject ho_ZReal,
        HObject ho_ZSub, HObject ho_RectLzs, HObject* ho_RegionMXs, HTuple hv_iModeJgPPSort,
        HTuple hv_iJgPPYStepPixel, HTuple hv_iModeJgPPZStepMode, HTuple hv_fJgPPZStepFix,
        HTuple hv_fJgPPZStepK, HTuple hv_fJgPPZStepB, HTuple hv_fJgLzUpOffset, HTuple hv_fJgDpUpOffset,
        HTuple* hv_ptsXList, HTuple* hv_ptsYList, HTuple* hv_ptsZList, HTuple* hv_ptsDefList,
        HTuple* hv_ptsRowList, HTuple* hv_ptsColList);


    void  trans_pose_face_x(HTuple hv_Pose1, HTuple hv_bFaceOrg, HTuple* hv_Pose2);


    void connection_3d_region_by_dis_x(HObject ho_X, HObject ho_Y, HObject ho_Z, HObject ho_Region,
        HObject* ho_RegionPart, HObject* ho_RectPart, HTuple hv_Dis);
};

