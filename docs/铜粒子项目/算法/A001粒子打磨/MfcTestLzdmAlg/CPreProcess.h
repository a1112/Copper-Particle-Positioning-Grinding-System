#pragma once


#include "DataX.h"

class CPreProcess
{

public:
    CPreProcess();
    virtual ~CPreProcess();

public:
    s_Rtnf OnPreProcess(s_Image3dS sImage3dS, s_PreProcess3DSPara spara1, s_PreProcess3DSResultPara& spara2);


};

