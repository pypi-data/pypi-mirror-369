"""Wrapper around driver library.
   Class will setup the correct ctypes information for every function on first call.
"""

import ctypes
import threading
from typing import Any

import nirfmxspecan.errors as errors
import nirfmxspecan.internal._custom_types as _custom_types


class Library(object):
    """Library

    Wrapper around driver library.
    Class will setup the correct ctypes information for every function on first call.
    """

    def __init__(self, ctypes_library):
        """Initialize the Library object."""
        self._func_lock = threading.Lock()
        self._library = ctypes_library
        # We cache the cfunc object from the ctypes.CDLL object
        self.RFmxSpecAn_ResetAttribute_cfunc = None
        self.RFmxSpecAn_GetError_cfunc = None
        self.RFmxSpecAn_GetErrorString_cfunc = None
        self.RFmxSpecAn_GetAttributeI8_cfunc = None
        self.RFmxSpecAn_SetAttributeI8_cfunc = None
        self.RFmxSpecAn_GetAttributeI8Array_cfunc = None
        self.RFmxSpecAn_SetAttributeI8Array_cfunc = None
        self.RFmxSpecAn_GetAttributeI16_cfunc = None
        self.RFmxSpecAn_SetAttributeI16_cfunc = None
        self.RFmxSpecAn_GetAttributeI32_cfunc = None
        self.RFmxSpecAn_SetAttributeI32_cfunc = None
        self.RFmxSpecAn_GetAttributeI32Array_cfunc = None
        self.RFmxSpecAn_SetAttributeI32Array_cfunc = None
        self.RFmxSpecAn_GetAttributeI64_cfunc = None
        self.RFmxSpecAn_SetAttributeI64_cfunc = None
        self.RFmxSpecAn_GetAttributeI64Array_cfunc = None
        self.RFmxSpecAn_SetAttributeI64Array_cfunc = None
        self.RFmxSpecAn_GetAttributeU8_cfunc = None
        self.RFmxSpecAn_SetAttributeU8_cfunc = None
        self.RFmxSpecAn_GetAttributeU8Array_cfunc = None
        self.RFmxSpecAn_SetAttributeU8Array_cfunc = None
        self.RFmxSpecAn_GetAttributeU16_cfunc = None
        self.RFmxSpecAn_SetAttributeU16_cfunc = None
        self.RFmxSpecAn_GetAttributeU32_cfunc = None
        self.RFmxSpecAn_SetAttributeU32_cfunc = None
        self.RFmxSpecAn_GetAttributeU32Array_cfunc = None
        self.RFmxSpecAn_SetAttributeU32Array_cfunc = None
        self.RFmxSpecAn_GetAttributeU64Array_cfunc = None
        self.RFmxSpecAn_SetAttributeU64Array_cfunc = None
        self.RFmxSpecAn_GetAttributeF32_cfunc = None
        self.RFmxSpecAn_SetAttributeF32_cfunc = None
        self.RFmxSpecAn_GetAttributeF32Array_cfunc = None
        self.RFmxSpecAn_SetAttributeF32Array_cfunc = None
        self.RFmxSpecAn_GetAttributeF64_cfunc = None
        self.RFmxSpecAn_SetAttributeF64_cfunc = None
        self.RFmxSpecAn_GetAttributeF64Array_cfunc = None
        self.RFmxSpecAn_SetAttributeF64Array_cfunc = None
        self.RFmxSpecAn_GetAttributeNIComplexSingleArray_cfunc = None
        self.RFmxSpecAn_SetAttributeNIComplexSingleArray_cfunc = None
        self.RFmxSpecAn_GetAttributeNIComplexDoubleArray_cfunc = None
        self.RFmxSpecAn_SetAttributeNIComplexDoubleArray_cfunc = None
        self.RFmxSpecAn_GetAttributeString_cfunc = None
        self.RFmxSpecAn_SetAttributeString_cfunc = None
        self.RFmxSpecAn_NFClearCalibrationDatabase_cfunc = None
        self.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints_cfunc = None
        self.RFmxSpecAn_NFCfgFrequencyList_StartStopStep_cfunc = None
        self.RFmxSpecAn_NFRecommendReferenceLevel_cfunc = None
        self.RFmxSpecAn_NFValidateCalibrationData_cfunc = None
        self.RFmxSpecAn_NFLoadDUTInputLossFromS2p_cfunc = None
        self.RFmxSpecAn_NFLoadDUTOutputLossFromS2p_cfunc = None
        self.RFmxSpecAn_NFLoadCalibrationLossFromS2p_cfunc = None
        self.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p_cfunc = None
        self.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p_cfunc = None
        self.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p_cfunc = None
        self.RFmxSpecAn_NFLoadExternalPreampGainFromS2p_cfunc = None
        self.RFmxSpecAn_SpectrumCfgFrequencyStartStop_cfunc = None
        self.RFmxSpecAn_SpectrumValidateNoiseCalibrationData_cfunc = None
        self.RFmxSpecAn_AMPMCfgReferenceWaveform_cfunc = None
        self.RFmxSpecAn_DPDApplyDigitalPredistortion_cfunc = None
        self.RFmxSpecAn_DPDApplyPreDPDSignalConditioning_cfunc = None
        self.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial_cfunc = None
        self.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable_cfunc = None
        self.RFmxSpecAn_DPDCfgPreviousDPDPolynomial_cfunc = None
        self.RFmxSpecAn_DPDCfgReferenceWaveform_cfunc = None
        self.RFmxSpecAn_DPDCfgExtractModelTargetWaveform_cfunc = None
        self.RFmxSpecAn_ACPCfgCarrierAndOffsets_cfunc = None
        self.RFmxSpecAn_ACPValidateNoiseCalibrationData_cfunc = None
        self.RFmxSpecAn_CHPValidateNoiseCalibrationData_cfunc = None
        self.RFmxSpecAn_MarkerCfgNumberOfMarkers_cfunc = None
        self.RFmxSpecAn_MarkerCfgPeakExcursion_cfunc = None
        self.RFmxSpecAn_MarkerCfgReferenceMarker_cfunc = None
        self.RFmxSpecAn_MarkerCfgThreshold_cfunc = None
        self.RFmxSpecAn_MarkerCfgTrace_cfunc = None
        self.RFmxSpecAn_MarkerCfgType_cfunc = None
        self.RFmxSpecAn_MarkerCfgXLocation_cfunc = None
        self.RFmxSpecAn_MarkerCfgYLocation_cfunc = None
        self.RFmxSpecAn_MarkerCfgFunctionType_cfunc = None
        self.RFmxSpecAn_MarkerCfgBandSpan_cfunc = None
        self.RFmxSpecAn_PAVTCfgSegmentStartTimeStep_cfunc = None
        self.RFmxSpecAn_IDPDCfgReferenceWaveform_cfunc = None
        self.RFmxSpecAn_IDPDCfgPredistortedWaveform_cfunc = None
        self.RFmxSpecAn_IDPDCfgEqualizerCoefficients_cfunc = None
        self.RFmxSpecAn_AbortMeasurements_cfunc = None
        self.RFmxSpecAn_AnalyzeIQ1Waveform_cfunc = None
        self.RFmxSpecAn_AnalyzeSpectrum1Waveform_cfunc = None
        self.RFmxSpecAn_AutoLevel_cfunc = None
        self.RFmxSpecAn_CheckMeasurementStatus_cfunc = None
        self.RFmxSpecAn_ClearAllNamedResults_cfunc = None
        self.RFmxSpecAn_ClearNamedResult_cfunc = None
        self.RFmxSpecAn_ClearNoiseCalibrationDatabase_cfunc = None
        self.RFmxSpecAn_CloneSignalConfiguration_cfunc = None
        self.RFmxSpecAn_Commit_cfunc = None
        self.RFmxSpecAn_CfgDigitalEdgeTrigger_cfunc = None
        self.RFmxSpecAn_CfgIQPowerEdgeTrigger_cfunc = None
        self.RFmxSpecAn_CfgSoftwareEdgeTrigger_cfunc = None
        self.RFmxSpecAn_CreateList_cfunc = None
        self.RFmxSpecAn_CreateListStep_cfunc = None
        self.RFmxSpecAn_CreateSignalConfiguration_cfunc = None
        self.RFmxSpecAn_DeleteList_cfunc = None
        self.RFmxSpecAn_DeleteSignalConfiguration_cfunc = None
        self.RFmxSpecAn_DisableTrigger_cfunc = None
        self.RFmxSpecAn_GetAllNamedResultNames_cfunc = None
        self.RFmxSpecAn_Initiate_cfunc = None
        self.RFmxSpecAn_ResetToDefault_cfunc = None
        self.RFmxSpecAn_SelectMeasurements_cfunc = None
        self.RFmxSpecAn_SendSoftwareEdgeTrigger_cfunc = None
        self.RFmxSpecAn_WaitForMeasurementComplete_cfunc = None
        self.RFmxSpecAn_ValidateListStepNumber_cfunc = None
        self.RFmxSpecAn_IMCfgAutoIntermodsSetup_cfunc = None
        self.RFmxSpecAn_IMCfgAveraging_cfunc = None
        self.RFmxSpecAn_IMCfgFFT_cfunc = None
        self.RFmxSpecAn_IMCfgFrequencyDefinition_cfunc = None
        self.RFmxSpecAn_IMCfgFundamentalTones_cfunc = None
        self.RFmxSpecAn_IMCfgIntermodArray_cfunc = None
        self.RFmxSpecAn_IMCfgIntermod_cfunc = None
        self.RFmxSpecAn_IMCfgMeasurementMethod_cfunc = None
        self.RFmxSpecAn_IMCfgNumberOfIntermods_cfunc = None
        self.RFmxSpecAn_IMCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_IMCfgSweepTime_cfunc = None
        self.RFmxSpecAn_NFCfgAveraging_cfunc = None
        self.RFmxSpecAn_NFCfgCalibrationLoss_cfunc = None
        self.RFmxSpecAn_NFCfgColdSourceDUTSParameters_cfunc = None
        self.RFmxSpecAn_NFCfgColdSourceInputTermination_cfunc = None
        self.RFmxSpecAn_NFCfgColdSourceMode_cfunc = None
        self.RFmxSpecAn_NFCfgDUTInputLoss_cfunc = None
        self.RFmxSpecAn_NFCfgDUTOutputLoss_cfunc = None
        self.RFmxSpecAn_NFCfgFrequencyList_cfunc = None
        self.RFmxSpecAn_NFCfgMeasurementBandwidth_cfunc = None
        self.RFmxSpecAn_NFCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_NFCfgMeasurementMethod_cfunc = None
        self.RFmxSpecAn_NFCfgYFactorMode_cfunc = None
        self.RFmxSpecAn_NFCfgYFactorNoiseSourceENR_cfunc = None
        self.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss_cfunc = None
        self.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime_cfunc = None
        self.RFmxSpecAn_FCntCfgAveraging_cfunc = None
        self.RFmxSpecAn_FCntCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_FCntCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_FCntCfgThreshold_cfunc = None
        self.RFmxSpecAn_SpectrumCfgAveraging_cfunc = None
        self.RFmxSpecAn_SpectrumCfgDetector_cfunc = None
        self.RFmxSpecAn_SpectrumCfgFFT_cfunc = None
        self.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled_cfunc = None
        self.RFmxSpecAn_SpectrumCfgPowerUnits_cfunc = None
        self.RFmxSpecAn_SpectrumCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_SpectrumCfgSpan_cfunc = None
        self.RFmxSpecAn_SpectrumCfgSweepTime_cfunc = None
        self.RFmxSpecAn_SpectrumCfgVBWFilter_cfunc = None
        self.RFmxSpecAn_SpectrumCfgMeasurementMethod_cfunc = None
        self.RFmxSpecAn_SpurCfgAveraging_cfunc = None
        self.RFmxSpecAn_SpurCfgFFTWindowType_cfunc = None
        self.RFmxSpecAn_SpurCfgNumberOfRanges_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeAbsoluteLimit_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeDetectorArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeDetector_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeFrequencyArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeFrequency_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport_cfunc = None
        self.RFmxSpecAn_SpurCfgRangePeakCriteriaArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangePeakCriteria_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeRBWArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeRBWFilter_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeRelativeAttenuation_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeSweepTimeArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeSweepTime_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeVBWFilterArray_cfunc = None
        self.RFmxSpecAn_SpurCfgRangeVBWFilter_cfunc = None
        self.RFmxSpecAn_SpurCfgTraceRangeIndex_cfunc = None
        self.RFmxSpecAn_AMPMCfgAMToAMCurveFit_cfunc = None
        self.RFmxSpecAn_AMPMCfgAMToPMCurveFit_cfunc = None
        self.RFmxSpecAn_AMPMCfgAveraging_cfunc = None
        self.RFmxSpecAn_AMPMCfgCompressionPoints_cfunc = None
        self.RFmxSpecAn_AMPMCfgDUTAverageInputPower_cfunc = None
        self.RFmxSpecAn_AMPMCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_AMPMCfgMeasurementSampleRate_cfunc = None
        self.RFmxSpecAn_AMPMCfgReferencePowerType_cfunc = None
        self.RFmxSpecAn_AMPMCfgSynchronizationMethod_cfunc = None
        self.RFmxSpecAn_AMPMCfgThreshold_cfunc = None
        self.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput_cfunc = None
        self.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType_cfunc = None
        self.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType_cfunc = None
        self.RFmxSpecAn_DPDCfgAveraging_cfunc = None
        self.RFmxSpecAn_DPDCfgDPDModel_cfunc = None
        self.RFmxSpecAn_DPDCfgDUTAverageInputPower_cfunc = None
        self.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms_cfunc = None
        self.RFmxSpecAn_DPDCfgIterativeDPDEnabled_cfunc = None
        self.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit_cfunc = None
        self.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit_cfunc = None
        self.RFmxSpecAn_DPDCfgLookupTableStepSize_cfunc = None
        self.RFmxSpecAn_DPDCfgLookupTableThreshold_cfunc = None
        self.RFmxSpecAn_DPDCfgLookupTableType_cfunc = None
        self.RFmxSpecAn_DPDCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_DPDCfgMeasurementSampleRate_cfunc = None
        self.RFmxSpecAn_DPDCfgMemoryPolynomial_cfunc = None
        self.RFmxSpecAn_DPDCfgSynchronizationMethod_cfunc = None
        self.RFmxSpecAn_ACPCfgAveraging_cfunc = None
        self.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth_cfunc = None
        self.RFmxSpecAn_ACPCfgCarrierMode_cfunc = None
        self.RFmxSpecAn_ACPCfgCarrierFrequency_cfunc = None
        self.RFmxSpecAn_ACPCfgCarrierRRCFilter_cfunc = None
        self.RFmxSpecAn_ACPCfgFFT_cfunc = None
        self.RFmxSpecAn_ACPCfgMeasurementMethod_cfunc = None
        self.RFmxSpecAn_ACPCfgNoiseCompensationEnabled_cfunc = None
        self.RFmxSpecAn_ACPCfgNumberOfCarriers_cfunc = None
        self.RFmxSpecAn_ACPCfgNumberOfOffsets_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetArray_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetPowerReference_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetRRCFilterArray_cfunc = None
        self.RFmxSpecAn_ACPCfgOffsetRRCFilter_cfunc = None
        self.RFmxSpecAn_ACPCfgOffset_cfunc = None
        self.RFmxSpecAn_ACPCfgPowerUnits_cfunc = None
        self.RFmxSpecAn_ACPCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_ACPCfgSweepTime_cfunc = None
        self.RFmxSpecAn_ACPCfgDetector_cfunc = None
        self.RFmxSpecAn_CCDFCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_CCDFCfgNumberOfRecords_cfunc = None
        self.RFmxSpecAn_CCDFCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_CCDFCfgThreshold_cfunc = None
        self.RFmxSpecAn_CHPCfgAveraging_cfunc = None
        self.RFmxSpecAn_CHPCfgCarrierOffset_cfunc = None
        self.RFmxSpecAn_CHPCfgFFT_cfunc = None
        self.RFmxSpecAn_CHPCfgIntegrationBandwidth_cfunc = None
        self.RFmxSpecAn_CHPCfgNumberOfCarriers_cfunc = None
        self.RFmxSpecAn_CHPCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_CHPCfgRRCFilter_cfunc = None
        self.RFmxSpecAn_CHPCfgSpan_cfunc = None
        self.RFmxSpecAn_CHPCfgSweepTime_cfunc = None
        self.RFmxSpecAn_CHPCfgDetector_cfunc = None
        self.RFmxSpecAn_HarmCfgAutoHarmonics_cfunc = None
        self.RFmxSpecAn_HarmCfgAveraging_cfunc = None
        self.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval_cfunc = None
        self.RFmxSpecAn_HarmCfgFundamentalRBW_cfunc = None
        self.RFmxSpecAn_HarmCfgHarmonicArray_cfunc = None
        self.RFmxSpecAn_HarmCfgHarmonic_cfunc = None
        self.RFmxSpecAn_HarmCfgNumberOfHarmonics_cfunc = None
        self.RFmxSpecAn_SEMCfgAveraging_cfunc = None
        self.RFmxSpecAn_SEMCfgCarrierChannelBandwidth_cfunc = None
        self.RFmxSpecAn_SEMCfgCarrierEnabled_cfunc = None
        self.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth_cfunc = None
        self.RFmxSpecAn_SEMCfgCarrierFrequency_cfunc = None
        self.RFmxSpecAn_SEMCfgCarrierRBWFilter_cfunc = None
        self.RFmxSpecAn_SEMCfgCarrierRRCFilter_cfunc = None
        self.RFmxSpecAn_SEMCfgFFT_cfunc = None
        self.RFmxSpecAn_SEMCfgNumberOfCarriers_cfunc = None
        self.RFmxSpecAn_SEMCfgNumberOfOffsets_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetFrequencyArray_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetFrequency_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetLimitFailMask_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetRBWFilterArray_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetRBWFilter_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray_cfunc = None
        self.RFmxSpecAn_SEMCfgOffsetRelativeLimit_cfunc = None
        self.RFmxSpecAn_SEMCfgPowerUnits_cfunc = None
        self.RFmxSpecAn_SEMCfgReferenceType_cfunc = None
        self.RFmxSpecAn_SEMCfgSweepTime_cfunc = None
        self.RFmxSpecAn_OBWCfgAveraging_cfunc = None
        self.RFmxSpecAn_OBWCfgBandwidthPercentage_cfunc = None
        self.RFmxSpecAn_OBWCfgFFT_cfunc = None
        self.RFmxSpecAn_OBWCfgPowerUnits_cfunc = None
        self.RFmxSpecAn_OBWCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_OBWCfgSpan_cfunc = None
        self.RFmxSpecAn_OBWCfgSweepTime_cfunc = None
        self.RFmxSpecAn_TXPCfgAveraging_cfunc = None
        self.RFmxSpecAn_TXPCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_TXPCfgRBWFilter_cfunc = None
        self.RFmxSpecAn_TXPCfgThreshold_cfunc = None
        self.RFmxSpecAn_TXPCfgVBWFilter_cfunc = None
        self.RFmxSpecAn_IQCfgAcquisition_cfunc = None
        self.RFmxSpecAn_IQCfgBandwidth_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgAutoRange_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgCancellation_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgRangeArray_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgRangeDefinition_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgSmoothing_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList_cfunc = None
        self.RFmxSpecAn_PhaseNoiseCfgSpurRemoval_cfunc = None
        self.RFmxSpecAn_PAVTCfgMeasurementBandwidth_cfunc = None
        self.RFmxSpecAn_PAVTCfgMeasurementIntervalMode_cfunc = None
        self.RFmxSpecAn_PAVTCfgMeasurementInterval_cfunc = None
        self.RFmxSpecAn_PAVTCfgMeasurementLocationType_cfunc = None
        self.RFmxSpecAn_PAVTCfgNumberOfSegments_cfunc = None
        self.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray_cfunc = None
        self.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval_cfunc = None
        self.RFmxSpecAn_PAVTCfgSegmentStartTimeList_cfunc = None
        self.RFmxSpecAn_PAVTCfgSegmentTypeArray_cfunc = None
        self.RFmxSpecAn_PAVTCfgSegmentType_cfunc = None
        self.RFmxSpecAn_PowerListCfgRBWFilterArray_cfunc = None
        self.RFmxSpecAn_CfgExternalAttenuation_cfunc = None
        self.RFmxSpecAn_CfgFrequency_cfunc = None
        self.RFmxSpecAn_CfgReferenceLevel_cfunc = None
        self.RFmxSpecAn_CfgRF_cfunc = None
        self.RFmxSpecAn_IMFetchFundamentalMeasurement_cfunc = None
        self.RFmxSpecAn_IMFetchInterceptPower_cfunc = None
        self.RFmxSpecAn_IMFetchIntermodMeasurement_cfunc = None
        self.RFmxSpecAn_FCntFetchAllanDeviation_cfunc = None
        self.RFmxSpecAn_FCntFetchMeasurement_cfunc = None
        self.RFmxSpecAn_FCntRead_cfunc = None
        self.RFmxSpecAn_SpectrumFetchMeasurement_cfunc = None
        self.RFmxSpecAn_SpurFetchMeasurementStatus_cfunc = None
        self.RFmxSpecAn_SpurFetchRangeStatus_cfunc = None
        self.RFmxSpecAn_SpurFetchSpurMeasurement_cfunc = None
        self.RFmxSpecAn_AMPMFetchCurveFitResidual_cfunc = None
        self.RFmxSpecAn_AMPMFetchDUTCharacteristics_cfunc = None
        self.RFmxSpecAn_AMPMFetchError_cfunc = None
        self.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR_cfunc = None
        self.RFmxSpecAn_DPDFetchAverageGain_cfunc = None
        self.RFmxSpecAn_DPDFetchNMSE_cfunc = None
        self.RFmxSpecAn_ACPFetchCarrierMeasurement_cfunc = None
        self.RFmxSpecAn_ACPFetchFrequencyResolution_cfunc = None
        self.RFmxSpecAn_ACPFetchOffsetMeasurement_cfunc = None
        self.RFmxSpecAn_ACPFetchTotalCarrierPower_cfunc = None
        self.RFmxSpecAn_ACPRead_cfunc = None
        self.RFmxSpecAn_CCDFFetchBasicPowerProbabilities_cfunc = None
        self.RFmxSpecAn_CCDFFetchPower_cfunc = None
        self.RFmxSpecAn_CCDFRead_cfunc = None
        self.RFmxSpecAn_CHPFetchTotalCarrierPower_cfunc = None
        self.RFmxSpecAn_CHPRead_cfunc = None
        self.RFmxSpecAn_HarmFetchHarmonicMeasurement_cfunc = None
        self.RFmxSpecAn_HarmFetchTHD_cfunc = None
        self.RFmxSpecAn_HarmRead_cfunc = None
        self.RFmxSpecAn_MarkerFetchXY_cfunc = None
        self.RFmxSpecAn_MarkerNextPeak_cfunc = None
        self.RFmxSpecAn_MarkerPeakSearch_cfunc = None
        self.RFmxSpecAn_MarkerFetchFunctionValue_cfunc = None
        self.RFmxSpecAn_SEMFetchCarrierMeasurement_cfunc = None
        self.RFmxSpecAn_SEMFetchCompositeMeasurementStatus_cfunc = None
        self.RFmxSpecAn_SEMFetchFrequencyResolution_cfunc = None
        self.RFmxSpecAn_SEMFetchLowerOffsetMargin_cfunc = None
        self.RFmxSpecAn_SEMFetchLowerOffsetPower_cfunc = None
        self.RFmxSpecAn_SEMFetchTotalCarrierPower_cfunc = None
        self.RFmxSpecAn_SEMFetchUpperOffsetMargin_cfunc = None
        self.RFmxSpecAn_SEMFetchUpperOffsetPower_cfunc = None
        self.RFmxSpecAn_OBWFetchMeasurement_cfunc = None
        self.RFmxSpecAn_OBWRead_cfunc = None
        self.RFmxSpecAn_TXPFetchMeasurement_cfunc = None
        self.RFmxSpecAn_TXPRead_cfunc = None
        self.RFmxSpecAn_IQGetRecordsDone_cfunc = None
        self.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement_cfunc = None
        self.RFmxSpecAn_PAVTFetchPhaseAndAmplitude_cfunc = None
        self.RFmxSpecAn_CHPFetchCarrierMeasurement_cfunc = None
        self.RFmxSpecAn_IMFetchInterceptPowerArray_cfunc = None
        self.RFmxSpecAn_IMFetchIntermodMeasurementArray_cfunc = None
        self.RFmxSpecAn_IMFetchSpectrum_cfunc = None
        self.RFmxSpecAn_NFFetchAnalyzerNoiseFigure_cfunc = None
        self.RFmxSpecAn_NFFetchColdSourcePower_cfunc = None
        self.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain_cfunc = None
        self.RFmxSpecAn_NFFetchYFactorPowers_cfunc = None
        self.RFmxSpecAn_NFFetchYFactors_cfunc = None
        self.RFmxSpecAn_FCntFetchFrequencyTrace_cfunc = None
        self.RFmxSpecAn_FCntFetchPhaseTrace_cfunc = None
        self.RFmxSpecAn_FCntFetchPowerTrace_cfunc = None
        self.RFmxSpecAn_SpectrumFetchPowerTrace_cfunc = None
        self.RFmxSpecAn_SpectrumFetchSpectrum_cfunc = None
        self.RFmxSpecAn_SpectrumRead_cfunc = None
        self.RFmxSpecAn_SpurFetchAllSpurs_cfunc = None
        self.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace_cfunc = None
        self.RFmxSpecAn_SpurFetchRangeSpectrumTrace_cfunc = None
        self.RFmxSpecAn_SpurFetchRangeStatusArray_cfunc = None
        self.RFmxSpecAn_SpurFetchSpurMeasurementArray_cfunc = None
        self.RFmxSpecAn_AMPMFetchAMToAMTrace_cfunc = None
        self.RFmxSpecAn_AMPMFetchAMToPMTrace_cfunc = None
        self.RFmxSpecAn_AMPMFetchCompressionPoints_cfunc = None
        self.RFmxSpecAn_AMPMFetchCurveFitCoefficients_cfunc = None
        self.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform_cfunc = None
        self.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform_cfunc = None
        self.RFmxSpecAn_AMPMFetchRelativePhaseTrace_cfunc = None
        self.RFmxSpecAn_AMPMFetchRelativePowerTrace_cfunc = None
        self.RFmxSpecAn_DPDFetchDPDPolynomial_cfunc = None
        self.RFmxSpecAn_DPDFetchDVRModel_cfunc = None
        self.RFmxSpecAn_DPDFetchLookupTable_cfunc = None
        self.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform_cfunc = None
        self.RFmxSpecAn_DPDFetchProcessedReferenceWaveform_cfunc = None
        self.RFmxSpecAn_ACPFetchAbsolutePowersTrace_cfunc = None
        self.RFmxSpecAn_ACPFetchOffsetMeasurementArray_cfunc = None
        self.RFmxSpecAn_ACPFetchRelativePowersTrace_cfunc = None
        self.RFmxSpecAn_ACPFetchSpectrum_cfunc = None
        self.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace_cfunc = None
        self.RFmxSpecAn_CCDFFetchProbabilitiesTrace_cfunc = None
        self.RFmxSpecAn_CHPFetchSpectrum_cfunc = None
        self.RFmxSpecAn_HarmFetchHarmonicPowerTrace_cfunc = None
        self.RFmxSpecAn_HarmFetchHarmonicMeasurementArray_cfunc = None
        self.RFmxSpecAn_SEMFetchAbsoluteMaskTrace_cfunc = None
        self.RFmxSpecAn_SEMFetchLowerOffsetMarginArray_cfunc = None
        self.RFmxSpecAn_SEMFetchLowerOffsetPowerArray_cfunc = None
        self.RFmxSpecAn_SEMFetchRelativeMaskTrace_cfunc = None
        self.RFmxSpecAn_SEMFetchSpectrum_cfunc = None
        self.RFmxSpecAn_SEMFetchUpperOffsetMarginArray_cfunc = None
        self.RFmxSpecAn_SEMFetchUpperOffsetPowerArray_cfunc = None
        self.RFmxSpecAn_OBWFetchSpectrumTrace_cfunc = None
        self.RFmxSpecAn_TXPFetchPowerTrace_cfunc = None
        self.RFmxSpecAn_IQFetchData_cfunc = None
        self.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise_cfunc = None
        self.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace_cfunc = None
        self.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace_cfunc = None
        self.RFmxSpecAn_PhaseNoiseFetchSpotNoise_cfunc = None
        self.RFmxSpecAn_PAVTFetchAmplitudeTrace_cfunc = None
        self.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray_cfunc = None
        self.RFmxSpecAn_PAVTFetchPhaseTrace_cfunc = None
        self.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform_cfunc = None
        self.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform_cfunc = None
        self.RFmxSpecAn_IDPDFetchPredistortedWaveform_cfunc = None
        self.RFmxSpecAn_IDPDFetchEqualizerCoefficients_cfunc = None
        self.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform_cfunc = None
        self.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray_cfunc = None
        self.RFmxSpecAn_PowerListFetchMaximumPowerArray_cfunc = None
        self.RFmxSpecAn_PowerListFetchMinimumPowerArray_cfunc = None

    def _get_library_function(self, name: str) -> Any:
        try:
            function = getattr(self._library, name)
        except AttributeError as e:
            raise errors.DriverTooOldError() from e  # type: ignore
        return function

    def RFmxSpecAn_ResetAttribute(self, vi, selector_string, attribute_id):
        """RFmxSpecAn_ResetAttribute."""
        with self._func_lock:
            if self.RFmxSpecAn_ResetAttribute_cfunc is None:
                self.RFmxSpecAn_ResetAttribute_cfunc = self._get_library_function(
                    "RFmxSpecAn_ResetAttribute"
                )
                self.RFmxSpecAn_ResetAttribute_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ResetAttribute_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ResetAttribute_cfunc(vi, selector_string, attribute_id)

    def RFmxSpecAn_GetError(self, vi, error_code, error_description_buffer_size, error_description):
        """RFmxSpecAn_GetError."""
        with self._func_lock:
            if self.RFmxSpecAn_GetError_cfunc is None:
                self.RFmxSpecAn_GetError_cfunc = self._get_library_function("RFmxSpecAn_GetError")
                self.RFmxSpecAn_GetError_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_GetError_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetError_cfunc(
            vi, error_code, error_description_buffer_size, error_description
        )

    def RFmxSpecAn_GetErrorString(
        self, vi, error_code, error_description_buffer_size, error_description
    ):
        """RFmxSpecAn_GetErrorString."""
        with self._func_lock:
            if self.RFmxSpecAn_GetErrorString_cfunc is None:
                self.RFmxSpecAn_GetErrorString_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetErrorString"
                )
                self.RFmxSpecAn_GetErrorString_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_GetErrorString_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetErrorString_cfunc(
            vi, error_code, error_description_buffer_size, error_description
        )

    def RFmxSpecAn_GetAttributeI8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeI8."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI8_cfunc is None:
                self.RFmxSpecAn_GetAttributeI8_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI8"
                )
                self.RFmxSpecAn_GetAttributeI8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int8),
                ]
                self.RFmxSpecAn_GetAttributeI8_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeI8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeI8."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI8_cfunc is None:
                self.RFmxSpecAn_SetAttributeI8_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI8"
                )
                self.RFmxSpecAn_SetAttributeI8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int8,
                ]
                self.RFmxSpecAn_SetAttributeI8_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeI16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeI16."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI16_cfunc is None:
                self.RFmxSpecAn_GetAttributeI16_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI16"
                )
                self.RFmxSpecAn_GetAttributeI16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int16),
                ]
                self.RFmxSpecAn_GetAttributeI16_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeI16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeI16."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI16_cfunc is None:
                self.RFmxSpecAn_SetAttributeI16_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI16"
                )
                self.RFmxSpecAn_SetAttributeI16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int16,
                ]
                self.RFmxSpecAn_SetAttributeI16_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeI32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeI32."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI32_cfunc is None:
                self.RFmxSpecAn_GetAttributeI32_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI32"
                )
                self.RFmxSpecAn_GetAttributeI32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeI32_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeI32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeI32."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI32_cfunc is None:
                self.RFmxSpecAn_SetAttributeI32_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI32"
                )
                self.RFmxSpecAn_SetAttributeI32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SetAttributeI32_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeI64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeI64."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI64_cfunc is None:
                self.RFmxSpecAn_GetAttributeI64_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI64"
                )
                self.RFmxSpecAn_GetAttributeI64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int64),
                ]
                self.RFmxSpecAn_GetAttributeI64_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeI64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeI64."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI64_cfunc is None:
                self.RFmxSpecAn_SetAttributeI64_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI64"
                )
                self.RFmxSpecAn_SetAttributeI64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int64,
                ]
                self.RFmxSpecAn_SetAttributeI64_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeU8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeU8."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeU8_cfunc is None:
                self.RFmxSpecAn_GetAttributeU8_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeU8"
                )
                self.RFmxSpecAn_GetAttributeU8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint8),
                ]
                self.RFmxSpecAn_GetAttributeU8_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeU8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeU8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeU8."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeU8_cfunc is None:
                self.RFmxSpecAn_SetAttributeU8_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeU8"
                )
                self.RFmxSpecAn_SetAttributeU8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_uint8,
                ]
                self.RFmxSpecAn_SetAttributeU8_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeU8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeU16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeU16."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeU16_cfunc is None:
                self.RFmxSpecAn_GetAttributeU16_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeU16"
                )
                self.RFmxSpecAn_GetAttributeU16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint16),
                ]
                self.RFmxSpecAn_GetAttributeU16_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeU16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeU16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeU16."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeU16_cfunc is None:
                self.RFmxSpecAn_SetAttributeU16_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeU16"
                )
                self.RFmxSpecAn_SetAttributeU16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_uint16,
                ]
                self.RFmxSpecAn_SetAttributeU16_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeU16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeU32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeU32."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeU32_cfunc is None:
                self.RFmxSpecAn_GetAttributeU32_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeU32"
                )
                self.RFmxSpecAn_GetAttributeU32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32),
                ]
                self.RFmxSpecAn_GetAttributeU32_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeU32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeU32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeU32."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeU32_cfunc is None:
                self.RFmxSpecAn_SetAttributeU32_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeU32"
                )
                self.RFmxSpecAn_SetAttributeU32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeU32_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeU32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeF32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeF32."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeF32_cfunc is None:
                self.RFmxSpecAn_GetAttributeF32_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeF32"
                )
                self.RFmxSpecAn_GetAttributeF32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                ]
                self.RFmxSpecAn_GetAttributeF32_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeF32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeF32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeF32."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeF32_cfunc is None:
                self.RFmxSpecAn_SetAttributeF32_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeF32"
                )
                self.RFmxSpecAn_SetAttributeF32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_float,
                ]
                self.RFmxSpecAn_SetAttributeF32_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeF32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeF64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_GetAttributeF64."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeF64_cfunc is None:
                self.RFmxSpecAn_GetAttributeF64_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeF64"
                )
                self.RFmxSpecAn_GetAttributeF64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_GetAttributeF64_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeF64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_SetAttributeF64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeF64."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeF64_cfunc is None:
                self.RFmxSpecAn_SetAttributeF64_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeF64"
                )
                self.RFmxSpecAn_SetAttributeF64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SetAttributeF64_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeF64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_GetAttributeI8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeI8Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI8Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeI8Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI8Array"
                )
                self.RFmxSpecAn_GetAttributeI8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int8),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeI8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeI8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeI8Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI8Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeI8Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI8Array"
                )
                self.RFmxSpecAn_SetAttributeI8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int8),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeI8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeI32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeI32Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI32Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeI32Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI32Array"
                )
                self.RFmxSpecAn_GetAttributeI32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeI32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeI32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeI32Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI32Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeI32Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI32Array"
                )
                self.RFmxSpecAn_SetAttributeI32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeI32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeI64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeI64Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeI64Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeI64Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeI64Array"
                )
                self.RFmxSpecAn_GetAttributeI64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int64),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeI64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeI64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeI64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeI64Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeI64Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeI64Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeI64Array"
                )
                self.RFmxSpecAn_SetAttributeI64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int64),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeI64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeI64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeU8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeU8Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeU8Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeU8Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeU8Array"
                )
                self.RFmxSpecAn_GetAttributeU8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeU8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeU8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeU8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeU8Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeU8Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeU8Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeU8Array"
                )
                self.RFmxSpecAn_SetAttributeU8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeU8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeU8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeU32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeU32Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeU32Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeU32Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeU32Array"
                )
                self.RFmxSpecAn_GetAttributeU32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeU32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeU32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeU32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeU32Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeU32Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeU32Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeU32Array"
                )
                self.RFmxSpecAn_SetAttributeU32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeU32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeU32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeU64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeU64Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeU64Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeU64Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeU64Array"
                )
                self.RFmxSpecAn_GetAttributeU64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeU64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeU64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeU64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeU64Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeU64Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeU64Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeU64Array"
                )
                self.RFmxSpecAn_SetAttributeU64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeU64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeU64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeF32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeF32Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeF32Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeF32Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeF32Array"
                )
                self.RFmxSpecAn_GetAttributeF32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeF32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeF32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeF32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeF32Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeF32Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeF32Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeF32Array"
                )
                self.RFmxSpecAn_SetAttributeF32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeF32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeF32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeF64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeF64Array."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeF64Array_cfunc is None:
                self.RFmxSpecAn_GetAttributeF64Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeF64Array"
                )
                self.RFmxSpecAn_GetAttributeF64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeF64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeF64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeF64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeF64Array."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeF64Array_cfunc is None:
                self.RFmxSpecAn_SetAttributeF64Array_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeF64Array"
                )
                self.RFmxSpecAn_SetAttributeF64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeF64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeF64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeNIComplexSingleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeNIComplexSingleArray."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeNIComplexSingleArray_cfunc is None:
                self.RFmxSpecAn_GetAttributeNIComplexSingleArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeNIComplexSingleArray"
                )
                self.RFmxSpecAn_GetAttributeNIComplexSingleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeNIComplexSingleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeNIComplexSingleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeNIComplexSingleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeNIComplexSingleArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeNIComplexSingleArray_cfunc is None:
                self.RFmxSpecAn_SetAttributeNIComplexSingleArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeNIComplexSingleArray"
                )
                self.RFmxSpecAn_SetAttributeNIComplexSingleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeNIComplexSingleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeNIComplexSingleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeNIComplexDoubleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxSpecAn_GetAttributeNIComplexDoubleArray."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeNIComplexDoubleArray_cfunc is None:
                self.RFmxSpecAn_GetAttributeNIComplexDoubleArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeNIComplexDoubleArray"
                )
                self.RFmxSpecAn_GetAttributeNIComplexDoubleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAttributeNIComplexDoubleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeNIComplexDoubleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxSpecAn_SetAttributeNIComplexDoubleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxSpecAn_SetAttributeNIComplexDoubleArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeNIComplexDoubleArray_cfunc is None:
                self.RFmxSpecAn_SetAttributeNIComplexDoubleArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeNIComplexDoubleArray"
                )
                self.RFmxSpecAn_SetAttributeNIComplexDoubleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_uint32,
                ]
                self.RFmxSpecAn_SetAttributeNIComplexDoubleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeNIComplexDoubleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxSpecAn_GetAttributeString(
        self, vi, selector_string, attribute_id, array_size, attr_val
    ):
        """RFmxSpecAn_GetAttributeString."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAttributeString_cfunc is None:
                self.RFmxSpecAn_GetAttributeString_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAttributeString"
                )
                self.RFmxSpecAn_GetAttributeString_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_GetAttributeString_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAttributeString_cfunc(
            vi, selector_string, attribute_id, array_size, attr_val
        )

    def RFmxSpecAn_SetAttributeString(self, vi, selector_string, attribute_id, attr_val):
        """RFmxSpecAn_SetAttributeString."""
        with self._func_lock:
            if self.RFmxSpecAn_SetAttributeString_cfunc is None:
                self.RFmxSpecAn_SetAttributeString_cfunc = self._get_library_function(
                    "RFmxSpecAn_SetAttributeString"
                )
                self.RFmxSpecAn_SetAttributeString_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_SetAttributeString_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SetAttributeString_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxSpecAn_NFClearCalibrationDatabase(self, vi, calibration_setup_id):
        """RFmxSpecAn_NFClearCalibrationDatabase."""
        with self._func_lock:
            if self.RFmxSpecAn_NFClearCalibrationDatabase_cfunc is None:
                self.RFmxSpecAn_NFClearCalibrationDatabase_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFClearCalibrationDatabase"
                )
                self.RFmxSpecAn_NFClearCalibrationDatabase_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_NFClearCalibrationDatabase_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFClearCalibrationDatabase_cfunc(vi, calibration_setup_id)

    def RFmxSpecAn_NFCfgFrequencyList_StartStopPoints(
        self, vi, selector_string, start_frequency, stop_frequency, number_of_points
    ):
        """RFmxSpecAn_NFCfgFrequencyList_StartStopPoints."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints_cfunc is None:
                self.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints_cfunc = (
                    self._get_library_function("RFmxSpecAn_NFCfgFrequencyList_StartStopPoints")
                )
                self.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints_cfunc(
            vi, selector_string, start_frequency, stop_frequency, number_of_points
        )

    def RFmxSpecAn_NFCfgFrequencyList_StartStopStep(
        self, vi, selector_string, start_frequency, stop_frequency, step_size
    ):
        """RFmxSpecAn_NFCfgFrequencyList_StartStopStep."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgFrequencyList_StartStopStep_cfunc is None:
                self.RFmxSpecAn_NFCfgFrequencyList_StartStopStep_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgFrequencyList_StartStopStep"
                )
                self.RFmxSpecAn_NFCfgFrequencyList_StartStopStep_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFCfgFrequencyList_StartStopStep_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgFrequencyList_StartStopStep_cfunc(
            vi, selector_string, start_frequency, stop_frequency, step_size
        )

    def RFmxSpecAn_NFRecommendReferenceLevel(
        self, vi, selector_string, dut_max_gain, dut_max_noise_figure, reference_level
    ):
        """RFmxSpecAn_NFRecommendReferenceLevel."""
        with self._func_lock:
            if self.RFmxSpecAn_NFRecommendReferenceLevel_cfunc is None:
                self.RFmxSpecAn_NFRecommendReferenceLevel_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFRecommendReferenceLevel"
                )
                self.RFmxSpecAn_NFRecommendReferenceLevel_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_NFRecommendReferenceLevel_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFRecommendReferenceLevel_cfunc(
            vi, selector_string, dut_max_gain, dut_max_noise_figure, reference_level
        )

    def RFmxSpecAn_NFValidateCalibrationData(self, vi, selector_string, calibration_data_valid):
        """RFmxSpecAn_NFValidateCalibrationData."""
        with self._func_lock:
            if self.RFmxSpecAn_NFValidateCalibrationData_cfunc is None:
                self.RFmxSpecAn_NFValidateCalibrationData_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFValidateCalibrationData"
                )
                self.RFmxSpecAn_NFValidateCalibrationData_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_NFValidateCalibrationData_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFValidateCalibrationData_cfunc(
            vi, selector_string, calibration_data_valid
        )

    def RFmxSpecAn_NFLoadDUTInputLossFromS2p(
        self,
        vi,
        selector_string,
        dut_input_loss_compensation_enabled,
        dut_input_loss_s2p_file_path,
        dut_input_loss_s_parameter_orientation,
        dut_input_loss_temperature,
    ):
        """RFmxSpecAn_NFLoadDUTInputLossFromS2p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadDUTInputLossFromS2p_cfunc is None:
                self.RFmxSpecAn_NFLoadDUTInputLossFromS2p_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFLoadDUTInputLossFromS2p"
                )
                self.RFmxSpecAn_NFLoadDUTInputLossFromS2p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFLoadDUTInputLossFromS2p_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFLoadDUTInputLossFromS2p_cfunc(
            vi,
            selector_string,
            dut_input_loss_compensation_enabled,
            dut_input_loss_s2p_file_path,
            dut_input_loss_s_parameter_orientation,
            dut_input_loss_temperature,
        )

    def RFmxSpecAn_NFLoadDUTOutputLossFromS2p(
        self,
        vi,
        selector_string,
        dut_output_loss_compensation_enabled,
        dut_output_loss_s2p_file_path,
        dut_output_loss_s_parameter_orientation,
        dut_output_loss_temperature,
    ):
        """RFmxSpecAn_NFLoadDUTOutputLossFromS2p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadDUTOutputLossFromS2p_cfunc is None:
                self.RFmxSpecAn_NFLoadDUTOutputLossFromS2p_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFLoadDUTOutputLossFromS2p"
                )
                self.RFmxSpecAn_NFLoadDUTOutputLossFromS2p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFLoadDUTOutputLossFromS2p_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFLoadDUTOutputLossFromS2p_cfunc(
            vi,
            selector_string,
            dut_output_loss_compensation_enabled,
            dut_output_loss_s2p_file_path,
            dut_output_loss_s_parameter_orientation,
            dut_output_loss_temperature,
        )

    def RFmxSpecAn_NFLoadCalibrationLossFromS2p(
        self,
        vi,
        selector_string,
        calibration_loss_compensation_enabled,
        calibration_loss_s2p_file_path,
        calibration_loss_s_parameter_orientation,
        calibration_loss_temperature,
    ):
        """RFmxSpecAn_NFLoadCalibrationLossFromS2p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadCalibrationLossFromS2p_cfunc is None:
                self.RFmxSpecAn_NFLoadCalibrationLossFromS2p_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFLoadCalibrationLossFromS2p"
                )
                self.RFmxSpecAn_NFLoadCalibrationLossFromS2p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFLoadCalibrationLossFromS2p_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFLoadCalibrationLossFromS2p_cfunc(
            vi,
            selector_string,
            calibration_loss_compensation_enabled,
            calibration_loss_s2p_file_path,
            calibration_loss_s_parameter_orientation,
            calibration_loss_temperature,
        )

    def RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p(
        self, vi, selector_string, dut_s_parameters_s2p_file_path, dut_s_parameter_orientation
    ):
        """RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p_cfunc is None:
                self.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p_cfunc = (
                    self._get_library_function("RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p")
                )
                self.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p_cfunc(
            vi, selector_string, dut_s_parameters_s2p_file_path, dut_s_parameter_orientation
        )

    def RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p(
        self,
        vi,
        selector_string,
        noise_source_loss_compensation_enabled,
        noise_source_loss_s2p_file_path,
        noise_source_loss_s_parameter_orientation,
        noise_source_loss_temperature,
    ):
        """RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p_cfunc is None:
                self.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p_cfunc = (
                    self._get_library_function("RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p")
                )
                self.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p_cfunc(
            vi,
            selector_string,
            noise_source_loss_compensation_enabled,
            noise_source_loss_s2p_file_path,
            noise_source_loss_s_parameter_orientation,
            noise_source_loss_temperature,
        )

    def RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p(
        self, vi, selector_string, termination_s1p_file_path, termination_temperature
    ):
        """RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p_cfunc is None:
                self.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p_cfunc = (
                    self._get_library_function("RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p")
                )
                self.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p_cfunc(
            vi, selector_string, termination_s1p_file_path, termination_temperature
        )

    def RFmxSpecAn_NFLoadExternalPreampGainFromS2p(
        self,
        vi,
        selector_string,
        external_preamp_present,
        external_preamp_gain_s2p_file_path,
        external_preamp_gain_s_parameter_orientation,
    ):
        """RFmxSpecAn_NFLoadExternalPreampGainFromS2p."""
        with self._func_lock:
            if self.RFmxSpecAn_NFLoadExternalPreampGainFromS2p_cfunc is None:
                self.RFmxSpecAn_NFLoadExternalPreampGainFromS2p_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFLoadExternalPreampGainFromS2p"
                )
                self.RFmxSpecAn_NFLoadExternalPreampGainFromS2p_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFLoadExternalPreampGainFromS2p_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFLoadExternalPreampGainFromS2p_cfunc(
            vi,
            selector_string,
            external_preamp_present,
            external_preamp_gain_s2p_file_path,
            external_preamp_gain_s_parameter_orientation,
        )

    def RFmxSpecAn_SpectrumCfgFrequencyStartStop(
        self, vi, selector_string, start_frequency, stop_frequency
    ):
        """RFmxSpecAn_SpectrumCfgFrequencyStartStop."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgFrequencyStartStop_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgFrequencyStartStop_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgFrequencyStartStop"
                )
                self.RFmxSpecAn_SpectrumCfgFrequencyStartStop_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpectrumCfgFrequencyStartStop_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgFrequencyStartStop_cfunc(
            vi, selector_string, start_frequency, stop_frequency
        )

    def RFmxSpecAn_SpectrumValidateNoiseCalibrationData(
        self, vi, selector_string, noise_calibration_data_valid
    ):
        """RFmxSpecAn_SpectrumValidateNoiseCalibrationData."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumValidateNoiseCalibrationData_cfunc is None:
                self.RFmxSpecAn_SpectrumValidateNoiseCalibrationData_cfunc = (
                    self._get_library_function("RFmxSpecAn_SpectrumValidateNoiseCalibrationData")
                )
                self.RFmxSpecAn_SpectrumValidateNoiseCalibrationData_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpectrumValidateNoiseCalibrationData_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumValidateNoiseCalibrationData_cfunc(
            vi, selector_string, noise_calibration_data_valid
        )

    def RFmxSpecAn_AMPMCfgReferenceWaveform(
        self,
        vi,
        selector_string,
        x0,
        dx,
        reference_waveform,
        array_size,
        idle_duration_present,
        signal_type,
    ):
        """RFmxSpecAn_AMPMCfgReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_AMPMCfgReferenceWaveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgReferenceWaveform"
                )
                self.RFmxSpecAn_AMPMCfgReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgReferenceWaveform_cfunc(
            vi,
            selector_string,
            x0,
            dx,
            reference_waveform,
            array_size,
            idle_duration_present,
            signal_type,
        )

    def RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial(
        self, vi, selector_string, dpd_polynomial, array_size
    ):
        """RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial_cfunc is None:
                self.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial"
                )
                self.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial_cfunc(
            vi, selector_string, dpd_polynomial, array_size
        )

    def RFmxSpecAn_DPDCfgApplyDPDUserLookupTable(
        self, vi, selector_string, lut_input_powers, lut_complex_gains, array_size
    ):
        """RFmxSpecAn_DPDCfgApplyDPDUserLookupTable."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable_cfunc is None:
                self.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgApplyDPDUserLookupTable"
                )
                self.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable_cfunc(
            vi, selector_string, lut_input_powers, lut_complex_gains, array_size
        )

    def RFmxSpecAn_DPDCfgPreviousDPDPolynomial(
        self, vi, selector_string, previous_dpd_polynomial, array_size
    ):
        """RFmxSpecAn_DPDCfgPreviousDPDPolynomial."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgPreviousDPDPolynomial_cfunc is None:
                self.RFmxSpecAn_DPDCfgPreviousDPDPolynomial_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgPreviousDPDPolynomial"
                )
                self.RFmxSpecAn_DPDCfgPreviousDPDPolynomial_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgPreviousDPDPolynomial_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgPreviousDPDPolynomial_cfunc(
            vi, selector_string, previous_dpd_polynomial, array_size
        )

    def RFmxSpecAn_DPDCfgReferenceWaveform(
        self,
        vi,
        selector_string,
        x0,
        dx,
        reference_waveform,
        array_size,
        idle_duration_present,
        signal_type,
    ):
        """RFmxSpecAn_DPDCfgReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_DPDCfgReferenceWaveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgReferenceWaveform"
                )
                self.RFmxSpecAn_DPDCfgReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgReferenceWaveform_cfunc(
            vi,
            selector_string,
            x0,
            dx,
            reference_waveform,
            array_size,
            idle_duration_present,
            signal_type,
        )

    def RFmxSpecAn_DPDCfgExtractModelTargetWaveform(
        self, vi, selector_string, x0, dx, target_waveform, array_size
    ):
        """RFmxSpecAn_DPDCfgExtractModelTargetWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgExtractModelTargetWaveform_cfunc is None:
                self.RFmxSpecAn_DPDCfgExtractModelTargetWaveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgExtractModelTargetWaveform"
                )
                self.RFmxSpecAn_DPDCfgExtractModelTargetWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgExtractModelTargetWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgExtractModelTargetWaveform_cfunc(
            vi, selector_string, x0, dx, target_waveform, array_size
        )

    def RFmxSpecAn_ACPCfgCarrierAndOffsets(
        self, vi, selector_string, integration_bandwidth, number_of_offsets, channel_spacing
    ):
        """RFmxSpecAn_ACPCfgCarrierAndOffsets."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgCarrierAndOffsets_cfunc is None:
                self.RFmxSpecAn_ACPCfgCarrierAndOffsets_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgCarrierAndOffsets"
                )
                self.RFmxSpecAn_ACPCfgCarrierAndOffsets_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgCarrierAndOffsets_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgCarrierAndOffsets_cfunc(
            vi, selector_string, integration_bandwidth, number_of_offsets, channel_spacing
        )

    def RFmxSpecAn_ACPValidateNoiseCalibrationData(
        self, vi, selector_string, noise_calibration_data_valid
    ):
        """RFmxSpecAn_ACPValidateNoiseCalibrationData."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPValidateNoiseCalibrationData_cfunc is None:
                self.RFmxSpecAn_ACPValidateNoiseCalibrationData_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPValidateNoiseCalibrationData"
                )
                self.RFmxSpecAn_ACPValidateNoiseCalibrationData_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_ACPValidateNoiseCalibrationData_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPValidateNoiseCalibrationData_cfunc(
            vi, selector_string, noise_calibration_data_valid
        )

    def RFmxSpecAn_CHPValidateNoiseCalibrationData(
        self, vi, selector_string, noise_calibration_data_valid
    ):
        """RFmxSpecAn_CHPValidateNoiseCalibrationData."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPValidateNoiseCalibrationData_cfunc is None:
                self.RFmxSpecAn_CHPValidateNoiseCalibrationData_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPValidateNoiseCalibrationData"
                )
                self.RFmxSpecAn_CHPValidateNoiseCalibrationData_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CHPValidateNoiseCalibrationData_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPValidateNoiseCalibrationData_cfunc(
            vi, selector_string, noise_calibration_data_valid
        )

    def RFmxSpecAn_MarkerCfgNumberOfMarkers(self, vi, selector_string, number_of_markers):
        """RFmxSpecAn_MarkerCfgNumberOfMarkers."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgNumberOfMarkers_cfunc is None:
                self.RFmxSpecAn_MarkerCfgNumberOfMarkers_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgNumberOfMarkers"
                )
                self.RFmxSpecAn_MarkerCfgNumberOfMarkers_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_MarkerCfgNumberOfMarkers_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgNumberOfMarkers_cfunc(
            vi, selector_string, number_of_markers
        )

    def RFmxSpecAn_MarkerCfgPeakExcursion(
        self, vi, selector_string, peak_excursion_enabled, peak_excursion
    ):
        """RFmxSpecAn_MarkerCfgPeakExcursion."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgPeakExcursion_cfunc is None:
                self.RFmxSpecAn_MarkerCfgPeakExcursion_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgPeakExcursion"
                )
                self.RFmxSpecAn_MarkerCfgPeakExcursion_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_MarkerCfgPeakExcursion_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgPeakExcursion_cfunc(
            vi, selector_string, peak_excursion_enabled, peak_excursion
        )

    def RFmxSpecAn_MarkerCfgReferenceMarker(self, vi, selector_string, reference_marker):
        """RFmxSpecAn_MarkerCfgReferenceMarker."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgReferenceMarker_cfunc is None:
                self.RFmxSpecAn_MarkerCfgReferenceMarker_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgReferenceMarker"
                )
                self.RFmxSpecAn_MarkerCfgReferenceMarker_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_MarkerCfgReferenceMarker_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgReferenceMarker_cfunc(vi, selector_string, reference_marker)

    def RFmxSpecAn_MarkerCfgThreshold(self, vi, selector_string, threshold_enabled, threshold):
        """RFmxSpecAn_MarkerCfgThreshold."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgThreshold_cfunc is None:
                self.RFmxSpecAn_MarkerCfgThreshold_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgThreshold"
                )
                self.RFmxSpecAn_MarkerCfgThreshold_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_MarkerCfgThreshold_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgThreshold_cfunc(
            vi, selector_string, threshold_enabled, threshold
        )

    def RFmxSpecAn_MarkerCfgTrace(self, vi, selector_string, trace):
        """RFmxSpecAn_MarkerCfgTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgTrace_cfunc is None:
                self.RFmxSpecAn_MarkerCfgTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgTrace"
                )
                self.RFmxSpecAn_MarkerCfgTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_MarkerCfgTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgTrace_cfunc(vi, selector_string, trace)

    def RFmxSpecAn_MarkerCfgType(self, vi, selector_string, marker_type):
        """RFmxSpecAn_MarkerCfgType."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgType_cfunc is None:
                self.RFmxSpecAn_MarkerCfgType_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgType"
                )
                self.RFmxSpecAn_MarkerCfgType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_MarkerCfgType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgType_cfunc(vi, selector_string, marker_type)

    def RFmxSpecAn_MarkerCfgXLocation(self, vi, selector_string, marker_x_location):
        """RFmxSpecAn_MarkerCfgXLocation."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgXLocation_cfunc is None:
                self.RFmxSpecAn_MarkerCfgXLocation_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgXLocation"
                )
                self.RFmxSpecAn_MarkerCfgXLocation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_MarkerCfgXLocation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgXLocation_cfunc(vi, selector_string, marker_x_location)

    def RFmxSpecAn_MarkerCfgYLocation(self, vi, selector_string, marker_y_location):
        """RFmxSpecAn_MarkerCfgYLocation."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgYLocation_cfunc is None:
                self.RFmxSpecAn_MarkerCfgYLocation_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgYLocation"
                )
                self.RFmxSpecAn_MarkerCfgYLocation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_MarkerCfgYLocation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgYLocation_cfunc(vi, selector_string, marker_y_location)

    def RFmxSpecAn_MarkerCfgFunctionType(self, vi, selector_string, function_type):
        """RFmxSpecAn_MarkerCfgFunctionType."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgFunctionType_cfunc is None:
                self.RFmxSpecAn_MarkerCfgFunctionType_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgFunctionType"
                )
                self.RFmxSpecAn_MarkerCfgFunctionType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_MarkerCfgFunctionType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgFunctionType_cfunc(vi, selector_string, function_type)

    def RFmxSpecAn_MarkerCfgBandSpan(self, vi, selector_string, span):
        """RFmxSpecAn_MarkerCfgBandSpan."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerCfgBandSpan_cfunc is None:
                self.RFmxSpecAn_MarkerCfgBandSpan_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerCfgBandSpan"
                )
                self.RFmxSpecAn_MarkerCfgBandSpan_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_MarkerCfgBandSpan_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerCfgBandSpan_cfunc(vi, selector_string, span)

    def RFmxSpecAn_PAVTCfgSegmentStartTimeStep(
        self, vi, selector_string, number_of_segments, segment0_start_time, segment_interval
    ):
        """RFmxSpecAn_PAVTCfgSegmentStartTimeStep."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgSegmentStartTimeStep_cfunc is None:
                self.RFmxSpecAn_PAVTCfgSegmentStartTimeStep_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgSegmentStartTimeStep"
                )
                self.RFmxSpecAn_PAVTCfgSegmentStartTimeStep_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PAVTCfgSegmentStartTimeStep_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgSegmentStartTimeStep_cfunc(
            vi, selector_string, number_of_segments, segment0_start_time, segment_interval
        )

    def RFmxSpecAn_IDPDCfgReferenceWaveform(
        self,
        vi,
        selector_string,
        x0,
        dx,
        reference_waveform,
        array_size,
        idle_duration_present,
        signal_type,
    ):
        """RFmxSpecAn_IDPDCfgReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDCfgReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_IDPDCfgReferenceWaveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_IDPDCfgReferenceWaveform"
                )
                self.RFmxSpecAn_IDPDCfgReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IDPDCfgReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDCfgReferenceWaveform_cfunc(
            vi,
            selector_string,
            x0,
            dx,
            reference_waveform,
            array_size,
            idle_duration_present,
            signal_type,
        )

    def RFmxSpecAn_IDPDCfgPredistortedWaveform(
        self, vi, selector_string, x0, dx, predistorted_waveform, array_size, target_gain
    ):
        """RFmxSpecAn_IDPDCfgPredistortedWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDCfgPredistortedWaveform_cfunc is None:
                self.RFmxSpecAn_IDPDCfgPredistortedWaveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_IDPDCfgPredistortedWaveform"
                )
                self.RFmxSpecAn_IDPDCfgPredistortedWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_IDPDCfgPredistortedWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDCfgPredistortedWaveform_cfunc(
            vi, selector_string, x0, dx, predistorted_waveform, array_size, target_gain
        )

    def RFmxSpecAn_IDPDCfgEqualizerCoefficients(
        self, vi, selector_string, x0, dx, equalizer_coefficients, array_size
    ):
        """RFmxSpecAn_IDPDCfgEqualizerCoefficients."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDCfgEqualizerCoefficients_cfunc is None:
                self.RFmxSpecAn_IDPDCfgEqualizerCoefficients_cfunc = self._get_library_function(
                    "RFmxSpecAn_IDPDCfgEqualizerCoefficients"
                )
                self.RFmxSpecAn_IDPDCfgEqualizerCoefficients_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IDPDCfgEqualizerCoefficients_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDCfgEqualizerCoefficients_cfunc(
            vi, selector_string, x0, dx, equalizer_coefficients, array_size
        )

    def RFmxSpecAn_AbortMeasurements(self, vi, selector_string):
        """RFmxSpecAn_AbortMeasurements."""
        with self._func_lock:
            if self.RFmxSpecAn_AbortMeasurements_cfunc is None:
                self.RFmxSpecAn_AbortMeasurements_cfunc = self._get_library_function(
                    "RFmxSpecAn_AbortMeasurements"
                )
                self.RFmxSpecAn_AbortMeasurements_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_AbortMeasurements_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AbortMeasurements_cfunc(vi, selector_string)

    def RFmxSpecAn_AutoLevel(
        self, vi, selector_string, bandwidth, measurement_interval, reference_level
    ):
        """RFmxSpecAn_AutoLevel."""
        with self._func_lock:
            if self.RFmxSpecAn_AutoLevel_cfunc is None:
                self.RFmxSpecAn_AutoLevel_cfunc = self._get_library_function("RFmxSpecAn_AutoLevel")
                self.RFmxSpecAn_AutoLevel_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_AutoLevel_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AutoLevel_cfunc(
            vi, selector_string, bandwidth, measurement_interval, reference_level
        )

    def RFmxSpecAn_CheckMeasurementStatus(self, vi, selector_string, is_done):
        """RFmxSpecAn_CheckMeasurementStatus."""
        with self._func_lock:
            if self.RFmxSpecAn_CheckMeasurementStatus_cfunc is None:
                self.RFmxSpecAn_CheckMeasurementStatus_cfunc = self._get_library_function(
                    "RFmxSpecAn_CheckMeasurementStatus"
                )
                self.RFmxSpecAn_CheckMeasurementStatus_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CheckMeasurementStatus_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CheckMeasurementStatus_cfunc(vi, selector_string, is_done)

    def RFmxSpecAn_ClearAllNamedResults(self, vi, selector_string):
        """RFmxSpecAn_ClearAllNamedResults."""
        with self._func_lock:
            if self.RFmxSpecAn_ClearAllNamedResults_cfunc is None:
                self.RFmxSpecAn_ClearAllNamedResults_cfunc = self._get_library_function(
                    "RFmxSpecAn_ClearAllNamedResults"
                )
                self.RFmxSpecAn_ClearAllNamedResults_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_ClearAllNamedResults_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ClearAllNamedResults_cfunc(vi, selector_string)

    def RFmxSpecAn_ClearNamedResult(self, vi, selector_string):
        """RFmxSpecAn_ClearNamedResult."""
        with self._func_lock:
            if self.RFmxSpecAn_ClearNamedResult_cfunc is None:
                self.RFmxSpecAn_ClearNamedResult_cfunc = self._get_library_function(
                    "RFmxSpecAn_ClearNamedResult"
                )
                self.RFmxSpecAn_ClearNamedResult_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_ClearNamedResult_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ClearNamedResult_cfunc(vi, selector_string)

    def RFmxSpecAn_Commit(self, vi, selector_string):
        """RFmxSpecAn_Commit."""
        with self._func_lock:
            if self.RFmxSpecAn_Commit_cfunc is None:
                self.RFmxSpecAn_Commit_cfunc = self._get_library_function("RFmxSpecAn_Commit")
                self.RFmxSpecAn_Commit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_Commit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_Commit_cfunc(vi, selector_string)

    def RFmxSpecAn_CfgDigitalEdgeTrigger(
        self, vi, selector_string, digital_edge_source, digital_edge, trigger_delay, enable_trigger
    ):
        """RFmxSpecAn_CfgDigitalEdgeTrigger."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgDigitalEdgeTrigger_cfunc is None:
                self.RFmxSpecAn_CfgDigitalEdgeTrigger_cfunc = self._get_library_function(
                    "RFmxSpecAn_CfgDigitalEdgeTrigger"
                )
                self.RFmxSpecAn_CfgDigitalEdgeTrigger_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CfgDigitalEdgeTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgDigitalEdgeTrigger_cfunc(
            vi, selector_string, digital_edge_source, digital_edge, trigger_delay, enable_trigger
        )

    def RFmxSpecAn_CfgIQPowerEdgeTrigger(
        self,
        vi,
        selector_string,
        iq_power_edge_trigger_source,
        iq_power_edge_trigger_level,
        iq_power_edge_slope,
        trigger_delay,
        minimum_quiet_time_mode,
        minimum_quiet_time_duration,
        enable_trigger,
    ):
        """RFmxSpecAn_CfgIQPowerEdgeTrigger."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgIQPowerEdgeTrigger_cfunc is None:
                self.RFmxSpecAn_CfgIQPowerEdgeTrigger_cfunc = self._get_library_function(
                    "RFmxSpecAn_CfgIQPowerEdgeTrigger"
                )
                self.RFmxSpecAn_CfgIQPowerEdgeTrigger_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CfgIQPowerEdgeTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgIQPowerEdgeTrigger_cfunc(
            vi,
            selector_string,
            iq_power_edge_trigger_source,
            iq_power_edge_trigger_level,
            iq_power_edge_slope,
            trigger_delay,
            minimum_quiet_time_mode,
            minimum_quiet_time_duration,
            enable_trigger,
        )

    def RFmxSpecAn_CfgSoftwareEdgeTrigger(self, vi, selector_string, trigger_delay, enable_trigger):
        """RFmxSpecAn_CfgSoftwareEdgeTrigger."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgSoftwareEdgeTrigger_cfunc is None:
                self.RFmxSpecAn_CfgSoftwareEdgeTrigger_cfunc = self._get_library_function(
                    "RFmxSpecAn_CfgSoftwareEdgeTrigger"
                )
                self.RFmxSpecAn_CfgSoftwareEdgeTrigger_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CfgSoftwareEdgeTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgSoftwareEdgeTrigger_cfunc(
            vi, selector_string, trigger_delay, enable_trigger
        )

    def RFmxSpecAn_CreateList(self, vi, list_name):
        """RFmxSpecAn_CreateList."""
        with self._func_lock:
            if self.RFmxSpecAn_CreateList_cfunc is None:
                self.RFmxSpecAn_CreateList_cfunc = self._get_library_function(
                    "RFmxSpecAn_CreateList"
                )
                self.RFmxSpecAn_CreateList_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_CreateList_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CreateList_cfunc(vi, list_name)

    def RFmxSpecAn_CreateListStep(self, vi, selector_string, created_step_index):
        """RFmxSpecAn_CreateListStep."""
        with self._func_lock:
            if self.RFmxSpecAn_CreateListStep_cfunc is None:
                self.RFmxSpecAn_CreateListStep_cfunc = self._get_library_function(
                    "RFmxSpecAn_CreateListStep"
                )
                self.RFmxSpecAn_CreateListStep_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CreateListStep_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CreateListStep_cfunc(vi, selector_string, created_step_index)

    def RFmxSpecAn_CreateSignalConfiguration(self, vi, signal_name):
        """RFmxSpecAn_CreateSignalConfiguration."""
        with self._func_lock:
            if self.RFmxSpecAn_CreateSignalConfiguration_cfunc is None:
                self.RFmxSpecAn_CreateSignalConfiguration_cfunc = self._get_library_function(
                    "RFmxSpecAn_CreateSignalConfiguration"
                )
                self.RFmxSpecAn_CreateSignalConfiguration_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_CreateSignalConfiguration_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CreateSignalConfiguration_cfunc(vi, signal_name)

    def RFmxSpecAn_DeleteList(self, vi, list_name):
        """RFmxSpecAn_DeleteList."""
        with self._func_lock:
            if self.RFmxSpecAn_DeleteList_cfunc is None:
                self.RFmxSpecAn_DeleteList_cfunc = self._get_library_function(
                    "RFmxSpecAn_DeleteList"
                )
                self.RFmxSpecAn_DeleteList_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_DeleteList_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DeleteList_cfunc(vi, list_name)

    def RFmxSpecAn_DisableTrigger(self, vi, selector_string):
        """RFmxSpecAn_DisableTrigger."""
        with self._func_lock:
            if self.RFmxSpecAn_DisableTrigger_cfunc is None:
                self.RFmxSpecAn_DisableTrigger_cfunc = self._get_library_function(
                    "RFmxSpecAn_DisableTrigger"
                )
                self.RFmxSpecAn_DisableTrigger_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_DisableTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DisableTrigger_cfunc(vi, selector_string)

    def RFmxSpecAn_Initiate(self, vi, selector_string, result_name):
        """RFmxSpecAn_Initiate."""
        with self._func_lock:
            if self.RFmxSpecAn_Initiate_cfunc is None:
                self.RFmxSpecAn_Initiate_cfunc = self._get_library_function("RFmxSpecAn_Initiate")
                self.RFmxSpecAn_Initiate_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_Initiate_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_Initiate_cfunc(vi, selector_string, result_name)

    def RFmxSpecAn_ResetToDefault(self, vi, selector_string):
        """RFmxSpecAn_ResetToDefault."""
        with self._func_lock:
            if self.RFmxSpecAn_ResetToDefault_cfunc is None:
                self.RFmxSpecAn_ResetToDefault_cfunc = self._get_library_function(
                    "RFmxSpecAn_ResetToDefault"
                )
                self.RFmxSpecAn_ResetToDefault_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_ResetToDefault_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ResetToDefault_cfunc(vi, selector_string)

    def RFmxSpecAn_SelectMeasurements(self, vi, selector_string, measurements, enable_all_traces):
        """RFmxSpecAn_SelectMeasurements."""
        with self._func_lock:
            if self.RFmxSpecAn_SelectMeasurements_cfunc is None:
                self.RFmxSpecAn_SelectMeasurements_cfunc = self._get_library_function(
                    "RFmxSpecAn_SelectMeasurements"
                )
                self.RFmxSpecAn_SelectMeasurements_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SelectMeasurements_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SelectMeasurements_cfunc(
            vi, selector_string, measurements, enable_all_traces
        )

    def RFmxSpecAn_WaitForMeasurementComplete(self, vi, selector_string, timeout):
        """RFmxSpecAn_WaitForMeasurementComplete."""
        with self._func_lock:
            if self.RFmxSpecAn_WaitForMeasurementComplete_cfunc is None:
                self.RFmxSpecAn_WaitForMeasurementComplete_cfunc = self._get_library_function(
                    "RFmxSpecAn_WaitForMeasurementComplete"
                )
                self.RFmxSpecAn_WaitForMeasurementComplete_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_WaitForMeasurementComplete_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_WaitForMeasurementComplete_cfunc(vi, selector_string, timeout)

    def RFmxSpecAn_ValidateListStepNumber(self, vi, list_name, step_number):
        """RFmxSpecAn_ValidateListStepNumber."""
        with self._func_lock:
            if self.RFmxSpecAn_ValidateListStepNumber_cfunc is None:
                self.RFmxSpecAn_ValidateListStepNumber_cfunc = self._get_library_function(
                    "RFmxSpecAn_ValidateListStepNumber"
                )
                self.RFmxSpecAn_ValidateListStepNumber_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ValidateListStepNumber_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ValidateListStepNumber_cfunc(vi, list_name, step_number)

    def RFmxSpecAn_IMCfgAutoIntermodsSetup(
        self, vi, selector_string, auto_intermods_setup_enabled, maximum_intermod_order
    ):
        """RFmxSpecAn_IMCfgAutoIntermodsSetup."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgAutoIntermodsSetup_cfunc is None:
                self.RFmxSpecAn_IMCfgAutoIntermodsSetup_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgAutoIntermodsSetup"
                )
                self.RFmxSpecAn_IMCfgAutoIntermodsSetup_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgAutoIntermodsSetup_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgAutoIntermodsSetup_cfunc(
            vi, selector_string, auto_intermods_setup_enabled, maximum_intermod_order
        )

    def RFmxSpecAn_IMCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_IMCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgAveraging_cfunc is None:
                self.RFmxSpecAn_IMCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgAveraging"
                )
                self.RFmxSpecAn_IMCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_IMCfgFFT(self, vi, selector_string, fft_window, fft_padding):
        """RFmxSpecAn_IMCfgFFT."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgFFT_cfunc is None:
                self.RFmxSpecAn_IMCfgFFT_cfunc = self._get_library_function("RFmxSpecAn_IMCfgFFT")
                self.RFmxSpecAn_IMCfgFFT_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_IMCfgFFT_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgFFT_cfunc(vi, selector_string, fft_window, fft_padding)

    def RFmxSpecAn_IMCfgFrequencyDefinition(self, vi, selector_string, frequency_definition):
        """RFmxSpecAn_IMCfgFrequencyDefinition."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgFrequencyDefinition_cfunc is None:
                self.RFmxSpecAn_IMCfgFrequencyDefinition_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgFrequencyDefinition"
                )
                self.RFmxSpecAn_IMCfgFrequencyDefinition_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgFrequencyDefinition_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgFrequencyDefinition_cfunc(
            vi, selector_string, frequency_definition
        )

    def RFmxSpecAn_IMCfgFundamentalTones(
        self, vi, selector_string, lower_tone_frequency, upper_tone_frequency
    ):
        """RFmxSpecAn_IMCfgFundamentalTones."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgFundamentalTones_cfunc is None:
                self.RFmxSpecAn_IMCfgFundamentalTones_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgFundamentalTones"
                )
                self.RFmxSpecAn_IMCfgFundamentalTones_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_IMCfgFundamentalTones_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgFundamentalTones_cfunc(
            vi, selector_string, lower_tone_frequency, upper_tone_frequency
        )

    def RFmxSpecAn_IMCfgIntermodArray(
        self,
        vi,
        selector_string,
        intermod_order,
        lower_intermod_frequency,
        upper_intermod_frequency,
        intermod_side,
        intermod_enabled,
        number_of_elements,
    ):
        """RFmxSpecAn_IMCfgIntermodArray."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgIntermodArray_cfunc is None:
                self.RFmxSpecAn_IMCfgIntermodArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgIntermodArray"
                )
                self.RFmxSpecAn_IMCfgIntermodArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgIntermodArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgIntermodArray_cfunc(
            vi,
            selector_string,
            intermod_order,
            lower_intermod_frequency,
            upper_intermod_frequency,
            intermod_side,
            intermod_enabled,
            number_of_elements,
        )

    def RFmxSpecAn_IMCfgIntermod(
        self,
        vi,
        selector_string,
        intermod_order,
        lower_intermod_frequency,
        upper_intermod_frequency,
        intermod_side,
        intermod_enabled,
    ):
        """RFmxSpecAn_IMCfgIntermod."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgIntermod_cfunc is None:
                self.RFmxSpecAn_IMCfgIntermod_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgIntermod"
                )
                self.RFmxSpecAn_IMCfgIntermod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgIntermod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgIntermod_cfunc(
            vi,
            selector_string,
            intermod_order,
            lower_intermod_frequency,
            upper_intermod_frequency,
            intermod_side,
            intermod_enabled,
        )

    def RFmxSpecAn_IMCfgMeasurementMethod(self, vi, selector_string, measurement_method):
        """RFmxSpecAn_IMCfgMeasurementMethod."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgMeasurementMethod_cfunc is None:
                self.RFmxSpecAn_IMCfgMeasurementMethod_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgMeasurementMethod"
                )
                self.RFmxSpecAn_IMCfgMeasurementMethod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgMeasurementMethod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgMeasurementMethod_cfunc(vi, selector_string, measurement_method)

    def RFmxSpecAn_IMCfgNumberOfIntermods(self, vi, selector_string, number_of_intermods):
        """RFmxSpecAn_IMCfgNumberOfIntermods."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgNumberOfIntermods_cfunc is None:
                self.RFmxSpecAn_IMCfgNumberOfIntermods_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgNumberOfIntermods"
                )
                self.RFmxSpecAn_IMCfgNumberOfIntermods_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgNumberOfIntermods_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgNumberOfIntermods_cfunc(
            vi, selector_string, number_of_intermods
        )

    def RFmxSpecAn_IMCfgRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_IMCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_IMCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgRBWFilter"
                )
                self.RFmxSpecAn_IMCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_IMCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_IMCfgSweepTime(self, vi, selector_string, sweep_time_auto, sweep_time_interval):
        """RFmxSpecAn_IMCfgSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_IMCfgSweepTime_cfunc is None:
                self.RFmxSpecAn_IMCfgSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMCfgSweepTime"
                )
                self.RFmxSpecAn_IMCfgSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_IMCfgSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMCfgSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_NFCfgAveraging(self, vi, selector_string, averaging_enabled, averaging_count):
        """RFmxSpecAn_NFCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgAveraging_cfunc is None:
                self.RFmxSpecAn_NFCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgAveraging"
                )
                self.RFmxSpecAn_NFCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count
        )

    def RFmxSpecAn_NFCfgCalibrationLoss(
        self,
        vi,
        selector_string,
        calibration_loss_compensation_enabled,
        calibration_loss_frequency,
        calibration_loss,
        calibration_loss_temperature,
        array_size,
    ):
        """RFmxSpecAn_NFCfgCalibrationLoss."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgCalibrationLoss_cfunc is None:
                self.RFmxSpecAn_NFCfgCalibrationLoss_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgCalibrationLoss"
                )
                self.RFmxSpecAn_NFCfgCalibrationLoss_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgCalibrationLoss_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgCalibrationLoss_cfunc(
            vi,
            selector_string,
            calibration_loss_compensation_enabled,
            calibration_loss_frequency,
            calibration_loss,
            calibration_loss_temperature,
            array_size,
        )

    def RFmxSpecAn_NFCfgColdSourceDUTSParameters(
        self,
        vi,
        selector_string,
        dut_s_parameters_frequency,
        dut_s21,
        dut_s12,
        dut_s11,
        dut_s22,
        array_size,
    ):
        """RFmxSpecAn_NFCfgColdSourceDUTSParameters."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgColdSourceDUTSParameters_cfunc is None:
                self.RFmxSpecAn_NFCfgColdSourceDUTSParameters_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgColdSourceDUTSParameters"
                )
                self.RFmxSpecAn_NFCfgColdSourceDUTSParameters_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgColdSourceDUTSParameters_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgColdSourceDUTSParameters_cfunc(
            vi,
            selector_string,
            dut_s_parameters_frequency,
            dut_s21,
            dut_s12,
            dut_s11,
            dut_s22,
            array_size,
        )

    def RFmxSpecAn_NFCfgColdSourceInputTermination(
        self,
        vi,
        selector_string,
        termination_vswr,
        termination_vswr_frequency,
        termination_temperature,
        array_size,
    ):
        """RFmxSpecAn_NFCfgColdSourceInputTermination."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgColdSourceInputTermination_cfunc is None:
                self.RFmxSpecAn_NFCfgColdSourceInputTermination_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgColdSourceInputTermination"
                )
                self.RFmxSpecAn_NFCfgColdSourceInputTermination_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgColdSourceInputTermination_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgColdSourceInputTermination_cfunc(
            vi,
            selector_string,
            termination_vswr,
            termination_vswr_frequency,
            termination_temperature,
            array_size,
        )

    def RFmxSpecAn_NFCfgColdSourceMode(self, vi, selector_string, cold_source_mode):
        """RFmxSpecAn_NFCfgColdSourceMode."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgColdSourceMode_cfunc is None:
                self.RFmxSpecAn_NFCfgColdSourceMode_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgColdSourceMode"
                )
                self.RFmxSpecAn_NFCfgColdSourceMode_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgColdSourceMode_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgColdSourceMode_cfunc(vi, selector_string, cold_source_mode)

    def RFmxSpecAn_NFCfgDUTInputLoss(
        self,
        vi,
        selector_string,
        dut_input_loss_compensation_enabled,
        dut_input_loss_frequency,
        dut_input_loss,
        dut_input_loss_temperature,
        array_size,
    ):
        """RFmxSpecAn_NFCfgDUTInputLoss."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgDUTInputLoss_cfunc is None:
                self.RFmxSpecAn_NFCfgDUTInputLoss_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgDUTInputLoss"
                )
                self.RFmxSpecAn_NFCfgDUTInputLoss_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgDUTInputLoss_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgDUTInputLoss_cfunc(
            vi,
            selector_string,
            dut_input_loss_compensation_enabled,
            dut_input_loss_frequency,
            dut_input_loss,
            dut_input_loss_temperature,
            array_size,
        )

    def RFmxSpecAn_NFCfgDUTOutputLoss(
        self,
        vi,
        selector_string,
        dut_output_loss_compensation_enabled,
        dut_output_loss_frequency,
        dut_output_loss,
        dut_output_loss_temperature,
        array_size,
    ):
        """RFmxSpecAn_NFCfgDUTOutputLoss."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgDUTOutputLoss_cfunc is None:
                self.RFmxSpecAn_NFCfgDUTOutputLoss_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgDUTOutputLoss"
                )
                self.RFmxSpecAn_NFCfgDUTOutputLoss_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgDUTOutputLoss_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgDUTOutputLoss_cfunc(
            vi,
            selector_string,
            dut_output_loss_compensation_enabled,
            dut_output_loss_frequency,
            dut_output_loss,
            dut_output_loss_temperature,
            array_size,
        )

    def RFmxSpecAn_NFCfgFrequencyList(self, vi, selector_string, frequency_list, array_size):
        """RFmxSpecAn_NFCfgFrequencyList."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgFrequencyList_cfunc is None:
                self.RFmxSpecAn_NFCfgFrequencyList_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgFrequencyList"
                )
                self.RFmxSpecAn_NFCfgFrequencyList_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgFrequencyList_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgFrequencyList_cfunc(
            vi, selector_string, frequency_list, array_size
        )

    def RFmxSpecAn_NFCfgMeasurementBandwidth(self, vi, selector_string, measurement_bandwidth):
        """RFmxSpecAn_NFCfgMeasurementBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgMeasurementBandwidth_cfunc is None:
                self.RFmxSpecAn_NFCfgMeasurementBandwidth_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgMeasurementBandwidth"
                )
                self.RFmxSpecAn_NFCfgMeasurementBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFCfgMeasurementBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgMeasurementBandwidth_cfunc(
            vi, selector_string, measurement_bandwidth
        )

    def RFmxSpecAn_NFCfgMeasurementInterval(self, vi, selector_string, measurement_interval):
        """RFmxSpecAn_NFCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_NFCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgMeasurementInterval"
                )
                self.RFmxSpecAn_NFCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_NFCfgMeasurementMethod(self, vi, selector_string, measurement_method):
        """RFmxSpecAn_NFCfgMeasurementMethod."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgMeasurementMethod_cfunc is None:
                self.RFmxSpecAn_NFCfgMeasurementMethod_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgMeasurementMethod"
                )
                self.RFmxSpecAn_NFCfgMeasurementMethod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgMeasurementMethod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgMeasurementMethod_cfunc(vi, selector_string, measurement_method)

    def RFmxSpecAn_NFCfgYFactorMode(self, vi, selector_string, y_factor_mode):
        """RFmxSpecAn_NFCfgYFactorMode."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgYFactorMode_cfunc is None:
                self.RFmxSpecAn_NFCfgYFactorMode_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgYFactorMode"
                )
                self.RFmxSpecAn_NFCfgYFactorMode_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgYFactorMode_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgYFactorMode_cfunc(vi, selector_string, y_factor_mode)

    def RFmxSpecAn_NFCfgYFactorNoiseSourceENR(
        self, vi, selector_string, enr_frequency, enr, cold_temperature, off_temperature, array_size
    ):
        """RFmxSpecAn_NFCfgYFactorNoiseSourceENR."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgYFactorNoiseSourceENR_cfunc is None:
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceENR_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgYFactorNoiseSourceENR"
                )
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceENR_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceENR_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgYFactorNoiseSourceENR_cfunc(
            vi, selector_string, enr_frequency, enr, cold_temperature, off_temperature, array_size
        )

    def RFmxSpecAn_NFCfgYFactorNoiseSourceLoss(
        self,
        vi,
        selector_string,
        noise_source_loss_compensation_enabled,
        noise_source_loss_frequency,
        noise_source_loss,
        noise_source_loss_temperature,
        array_size,
    ):
        """RFmxSpecAn_NFCfgYFactorNoiseSourceLoss."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss_cfunc is None:
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFCfgYFactorNoiseSourceLoss"
                )
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss_cfunc(
            vi,
            selector_string,
            noise_source_loss_compensation_enabled,
            noise_source_loss_frequency,
            noise_source_loss,
            noise_source_loss_temperature,
            array_size,
        )

    def RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime(self, vi, selector_string, settling_time):
        """RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime."""
        with self._func_lock:
            if self.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime_cfunc is None:
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime_cfunc = (
                    self._get_library_function("RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime")
                )
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime_cfunc(
            vi, selector_string, settling_time
        )

    def RFmxSpecAn_FCntCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_FCntCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntCfgAveraging_cfunc is None:
                self.RFmxSpecAn_FCntCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntCfgAveraging"
                )
                self.RFmxSpecAn_FCntCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_FCntCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_FCntCfgMeasurementInterval(self, vi, selector_string, measurement_interval):
        """RFmxSpecAn_FCntCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_FCntCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntCfgMeasurementInterval"
                )
                self.RFmxSpecAn_FCntCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_FCntCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_FCntCfgRBWFilter(self, vi, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """RFmxSpecAn_FCntCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_FCntCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntCfgRBWFilter"
                )
                self.RFmxSpecAn_FCntCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_FCntCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntCfgRBWFilter_cfunc(
            vi, selector_string, rbw, rbw_filter_type, rrc_alpha
        )

    def RFmxSpecAn_FCntCfgThreshold(
        self, vi, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """RFmxSpecAn_FCntCfgThreshold."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntCfgThreshold_cfunc is None:
                self.RFmxSpecAn_FCntCfgThreshold_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntCfgThreshold"
                )
                self.RFmxSpecAn_FCntCfgThreshold_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_FCntCfgThreshold_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntCfgThreshold_cfunc(
            vi, selector_string, threshold_enabled, threshold_level, threshold_type
        )

    def RFmxSpecAn_SpectrumCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_SpectrumCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgAveraging_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgAveraging"
                )
                self.RFmxSpecAn_SpectrumCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpectrumCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_SpectrumCfgDetector(self, vi, selector_string, detector_type, detector_points):
        """RFmxSpecAn_SpectrumCfgDetector."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgDetector_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgDetector_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgDetector"
                )
                self.RFmxSpecAn_SpectrumCfgDetector_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpectrumCfgDetector_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgDetector_cfunc(
            vi, selector_string, detector_type, detector_points
        )

    def RFmxSpecAn_SpectrumCfgFFT(self, vi, selector_string, fft_window, fft_padding):
        """RFmxSpecAn_SpectrumCfgFFT."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgFFT_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgFFT_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgFFT"
                )
                self.RFmxSpecAn_SpectrumCfgFFT_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpectrumCfgFFT_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgFFT_cfunc(vi, selector_string, fft_window, fft_padding)

    def RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled(
        self, vi, selector_string, noise_compensation_enabled
    ):
        """RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled_cfunc = (
                    self._get_library_function("RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled")
                )
                self.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled_cfunc(
            vi, selector_string, noise_compensation_enabled
        )

    def RFmxSpecAn_SpectrumCfgPowerUnits(self, vi, selector_string, spectrum_power_units):
        """RFmxSpecAn_SpectrumCfgPowerUnits."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgPowerUnits_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgPowerUnits_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgPowerUnits"
                )
                self.RFmxSpecAn_SpectrumCfgPowerUnits_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpectrumCfgPowerUnits_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgPowerUnits_cfunc(
            vi, selector_string, spectrum_power_units
        )

    def RFmxSpecAn_SpectrumCfgRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_SpectrumCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgRBWFilter"
                )
                self.RFmxSpecAn_SpectrumCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpectrumCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_SpectrumCfgSpan(self, vi, selector_string, span):
        """RFmxSpecAn_SpectrumCfgSpan."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgSpan_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgSpan_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgSpan"
                )
                self.RFmxSpecAn_SpectrumCfgSpan_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpectrumCfgSpan_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgSpan_cfunc(vi, selector_string, span)

    def RFmxSpecAn_SpectrumCfgSweepTime(
        self, vi, selector_string, sweep_time_auto, sweep_time_interval
    ):
        """RFmxSpecAn_SpectrumCfgSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgSweepTime_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgSweepTime"
                )
                self.RFmxSpecAn_SpectrumCfgSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpectrumCfgSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_SpectrumCfgVBWFilter(self, vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        """RFmxSpecAn_SpectrumCfgVBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgVBWFilter_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgVBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgVBWFilter"
                )
                self.RFmxSpecAn_SpectrumCfgVBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpectrumCfgVBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgVBWFilter_cfunc(
            vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
        )

    def RFmxSpecAn_SpectrumCfgMeasurementMethod(self, vi, selector_string, measurement_method):
        """RFmxSpecAn_SpectrumCfgMeasurementMethod."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumCfgMeasurementMethod_cfunc is None:
                self.RFmxSpecAn_SpectrumCfgMeasurementMethod_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumCfgMeasurementMethod"
                )
                self.RFmxSpecAn_SpectrumCfgMeasurementMethod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpectrumCfgMeasurementMethod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumCfgMeasurementMethod_cfunc(
            vi, selector_string, measurement_method
        )

    def RFmxSpecAn_SpurCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_SpurCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgAveraging_cfunc is None:
                self.RFmxSpecAn_SpurCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgAveraging"
                )
                self.RFmxSpecAn_SpurCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_SpurCfgFFTWindowType(self, vi, selector_string, fft_window):
        """RFmxSpecAn_SpurCfgFFTWindowType."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgFFTWindowType_cfunc is None:
                self.RFmxSpecAn_SpurCfgFFTWindowType_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgFFTWindowType"
                )
                self.RFmxSpecAn_SpurCfgFFTWindowType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgFFTWindowType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgFFTWindowType_cfunc(vi, selector_string, fft_window)

    def RFmxSpecAn_SpurCfgNumberOfRanges(self, vi, selector_string, number_of_ranges):
        """RFmxSpecAn_SpurCfgNumberOfRanges."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgNumberOfRanges_cfunc is None:
                self.RFmxSpecAn_SpurCfgNumberOfRanges_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgNumberOfRanges"
                )
                self.RFmxSpecAn_SpurCfgNumberOfRanges_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgNumberOfRanges_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgNumberOfRanges_cfunc(vi, selector_string, number_of_ranges)

    def RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray(
        self,
        vi,
        selector_string,
        absolute_limit_mode,
        absolute_limit_start,
        absolute_limit_stop,
        number_of_elements,
    ):
        """RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray"
                )
                self.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray_cfunc(
            vi,
            selector_string,
            absolute_limit_mode,
            absolute_limit_start,
            absolute_limit_stop,
            number_of_elements,
        )

    def RFmxSpecAn_SpurCfgRangeAbsoluteLimit(
        self, vi, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        """RFmxSpecAn_SpurCfgRangeAbsoluteLimit."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeAbsoluteLimit_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeAbsoluteLimit_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeAbsoluteLimit"
                )
                self.RFmxSpecAn_SpurCfgRangeAbsoluteLimit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpurCfgRangeAbsoluteLimit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeAbsoluteLimit_cfunc(
            vi, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
        )

    def RFmxSpecAn_SpurCfgRangeDetectorArray(
        self, vi, selector_string, detector_type, detector_points, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangeDetectorArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeDetectorArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeDetectorArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeDetectorArray"
                )
                self.RFmxSpecAn_SpurCfgRangeDetectorArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeDetectorArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeDetectorArray_cfunc(
            vi, selector_string, detector_type, detector_points, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeDetector(self, vi, selector_string, detector_type, detector_points):
        """RFmxSpecAn_SpurCfgRangeDetector."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeDetector_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeDetector_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeDetector"
                )
                self.RFmxSpecAn_SpurCfgRangeDetector_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeDetector_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeDetector_cfunc(
            vi, selector_string, detector_type, detector_points
        )

    def RFmxSpecAn_SpurCfgRangeFrequencyArray(
        self,
        vi,
        selector_string,
        start_frequency,
        stop_frequency,
        range_enabled,
        number_of_elements,
    ):
        """RFmxSpecAn_SpurCfgRangeFrequencyArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeFrequencyArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeFrequencyArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeFrequencyArray"
                )
                self.RFmxSpecAn_SpurCfgRangeFrequencyArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeFrequencyArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeFrequencyArray_cfunc(
            vi, selector_string, start_frequency, stop_frequency, range_enabled, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeFrequency(
        self, vi, selector_string, start_frequency, stop_frequency, range_enabled
    ):
        """RFmxSpecAn_SpurCfgRangeFrequency."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeFrequency_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeFrequency_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeFrequency"
                )
                self.RFmxSpecAn_SpurCfgRangeFrequency_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeFrequency_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeFrequency_cfunc(
            vi, selector_string, start_frequency, stop_frequency, range_enabled
        )

    def RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray(
        self, vi, selector_string, number_of_spurs_to_report, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray")
                )
                self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray_cfunc(
            vi, selector_string, number_of_spurs_to_report, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport(
        self, vi, selector_string, number_of_spurs_to_report
    ):
        """RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport_cfunc = (
                    self._get_library_function("RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport")
                )
                self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport_cfunc(
            vi, selector_string, number_of_spurs_to_report
        )

    def RFmxSpecAn_SpurCfgRangePeakCriteriaArray(
        self, vi, selector_string, threshold, excursion, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangePeakCriteriaArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangePeakCriteriaArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangePeakCriteriaArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangePeakCriteriaArray"
                )
                self.RFmxSpecAn_SpurCfgRangePeakCriteriaArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangePeakCriteriaArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangePeakCriteriaArray_cfunc(
            vi, selector_string, threshold, excursion, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangePeakCriteria(self, vi, selector_string, threshold, excursion):
        """RFmxSpecAn_SpurCfgRangePeakCriteria."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangePeakCriteria_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangePeakCriteria_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangePeakCriteria"
                )
                self.RFmxSpecAn_SpurCfgRangePeakCriteria_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpurCfgRangePeakCriteria_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangePeakCriteria_cfunc(
            vi, selector_string, threshold, excursion
        )

    def RFmxSpecAn_SpurCfgRangeRBWArray(
        self, vi, selector_string, rbw_auto, rbw, rbw_filter_type, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangeRBWArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeRBWArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeRBWArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeRBWArray"
                )
                self.RFmxSpecAn_SpurCfgRangeRBWArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeRBWArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeRBWArray_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_SpurCfgRangeRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeRBWFilter_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeRBWFilter"
                )
                self.RFmxSpecAn_SpurCfgRangeRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray(
        self, vi, selector_string, relative_attenuation, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray")
                )
                self.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray_cfunc(
            vi, selector_string, relative_attenuation, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeRelativeAttenuation(self, vi, selector_string, relative_attenuation):
        """RFmxSpecAn_SpurCfgRangeRelativeAttenuation."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeRelativeAttenuation_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeRelativeAttenuation_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeRelativeAttenuation"
                )
                self.RFmxSpecAn_SpurCfgRangeRelativeAttenuation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpurCfgRangeRelativeAttenuation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeRelativeAttenuation_cfunc(
            vi, selector_string, relative_attenuation
        )

    def RFmxSpecAn_SpurCfgRangeSweepTimeArray(
        self, vi, selector_string, sweep_time_auto, sweep_time_interval, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangeSweepTimeArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeSweepTimeArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeSweepTimeArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeSweepTimeArray"
                )
                self.RFmxSpecAn_SpurCfgRangeSweepTimeArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeSweepTimeArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeSweepTimeArray_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeSweepTime(
        self, vi, selector_string, sweep_time_auto, sweep_time_interval
    ):
        """RFmxSpecAn_SpurCfgRangeSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeSweepTime_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeSweepTime"
                )
                self.RFmxSpecAn_SpurCfgRangeSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpurCfgRangeSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_SpurCfgRangeVBWFilterArray(
        self, vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio, number_of_elements
    ):
        """RFmxSpecAn_SpurCfgRangeVBWFilterArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeVBWFilterArray_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeVBWFilterArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeVBWFilterArray"
                )
                self.RFmxSpecAn_SpurCfgRangeVBWFilterArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgRangeVBWFilterArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeVBWFilterArray_cfunc(
            vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio, number_of_elements
        )

    def RFmxSpecAn_SpurCfgRangeVBWFilter(
        self, vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
    ):
        """RFmxSpecAn_SpurCfgRangeVBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgRangeVBWFilter_cfunc is None:
                self.RFmxSpecAn_SpurCfgRangeVBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgRangeVBWFilter"
                )
                self.RFmxSpecAn_SpurCfgRangeVBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SpurCfgRangeVBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgRangeVBWFilter_cfunc(
            vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
        )

    def RFmxSpecAn_SpurCfgTraceRangeIndex(self, vi, selector_string, trace_range_index):
        """RFmxSpecAn_SpurCfgTraceRangeIndex."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurCfgTraceRangeIndex_cfunc is None:
                self.RFmxSpecAn_SpurCfgTraceRangeIndex_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurCfgTraceRangeIndex"
                )
                self.RFmxSpecAn_SpurCfgTraceRangeIndex_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SpurCfgTraceRangeIndex_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurCfgTraceRangeIndex_cfunc(vi, selector_string, trace_range_index)

    def RFmxSpecAn_AMPMCfgAMToAMCurveFit(
        self, vi, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
    ):
        """RFmxSpecAn_AMPMCfgAMToAMCurveFit."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgAMToAMCurveFit_cfunc is None:
                self.RFmxSpecAn_AMPMCfgAMToAMCurveFit_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgAMToAMCurveFit"
                )
                self.RFmxSpecAn_AMPMCfgAMToAMCurveFit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgAMToAMCurveFit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgAMToAMCurveFit_cfunc(
            vi, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
        )

    def RFmxSpecAn_AMPMCfgAMToPMCurveFit(
        self, vi, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
    ):
        """RFmxSpecAn_AMPMCfgAMToPMCurveFit."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgAMToPMCurveFit_cfunc is None:
                self.RFmxSpecAn_AMPMCfgAMToPMCurveFit_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgAMToPMCurveFit"
                )
                self.RFmxSpecAn_AMPMCfgAMToPMCurveFit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgAMToPMCurveFit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgAMToPMCurveFit_cfunc(
            vi, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
        )

    def RFmxSpecAn_AMPMCfgAveraging(self, vi, selector_string, averaging_enabled, averaging_count):
        """RFmxSpecAn_AMPMCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgAveraging_cfunc is None:
                self.RFmxSpecAn_AMPMCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgAveraging"
                )
                self.RFmxSpecAn_AMPMCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count
        )

    def RFmxSpecAn_AMPMCfgCompressionPoints(
        self, vi, selector_string, compression_point_enabled, compression_level, array_size
    ):
        """RFmxSpecAn_AMPMCfgCompressionPoints."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgCompressionPoints_cfunc is None:
                self.RFmxSpecAn_AMPMCfgCompressionPoints_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgCompressionPoints"
                )
                self.RFmxSpecAn_AMPMCfgCompressionPoints_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgCompressionPoints_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgCompressionPoints_cfunc(
            vi, selector_string, compression_point_enabled, compression_level, array_size
        )

    def RFmxSpecAn_AMPMCfgDUTAverageInputPower(self, vi, selector_string, dut_average_input_power):
        """RFmxSpecAn_AMPMCfgDUTAverageInputPower."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgDUTAverageInputPower_cfunc is None:
                self.RFmxSpecAn_AMPMCfgDUTAverageInputPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgDUTAverageInputPower"
                )
                self.RFmxSpecAn_AMPMCfgDUTAverageInputPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_AMPMCfgDUTAverageInputPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgDUTAverageInputPower_cfunc(
            vi, selector_string, dut_average_input_power
        )

    def RFmxSpecAn_AMPMCfgMeasurementInterval(self, vi, selector_string, measurement_interval):
        """RFmxSpecAn_AMPMCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_AMPMCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgMeasurementInterval"
                )
                self.RFmxSpecAn_AMPMCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_AMPMCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_AMPMCfgMeasurementSampleRate(
        self, vi, selector_string, sample_rate_mode, sample_rate
    ):
        """RFmxSpecAn_AMPMCfgMeasurementSampleRate."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgMeasurementSampleRate_cfunc is None:
                self.RFmxSpecAn_AMPMCfgMeasurementSampleRate_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgMeasurementSampleRate"
                )
                self.RFmxSpecAn_AMPMCfgMeasurementSampleRate_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_AMPMCfgMeasurementSampleRate_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgMeasurementSampleRate_cfunc(
            vi, selector_string, sample_rate_mode, sample_rate
        )

    def RFmxSpecAn_AMPMCfgReferencePowerType(self, vi, selector_string, reference_power_type):
        """RFmxSpecAn_AMPMCfgReferencePowerType."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgReferencePowerType_cfunc is None:
                self.RFmxSpecAn_AMPMCfgReferencePowerType_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgReferencePowerType"
                )
                self.RFmxSpecAn_AMPMCfgReferencePowerType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgReferencePowerType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgReferencePowerType_cfunc(
            vi, selector_string, reference_power_type
        )

    def RFmxSpecAn_AMPMCfgSynchronizationMethod(self, vi, selector_string, synchronization_method):
        """RFmxSpecAn_AMPMCfgSynchronizationMethod."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgSynchronizationMethod_cfunc is None:
                self.RFmxSpecAn_AMPMCfgSynchronizationMethod_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgSynchronizationMethod"
                )
                self.RFmxSpecAn_AMPMCfgSynchronizationMethod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgSynchronizationMethod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgSynchronizationMethod_cfunc(
            vi, selector_string, synchronization_method
        )

    def RFmxSpecAn_AMPMCfgThreshold(
        self, vi, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """RFmxSpecAn_AMPMCfgThreshold."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMCfgThreshold_cfunc is None:
                self.RFmxSpecAn_AMPMCfgThreshold_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMCfgThreshold"
                )
                self.RFmxSpecAn_AMPMCfgThreshold_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_AMPMCfgThreshold_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMCfgThreshold_cfunc(
            vi, selector_string, threshold_enabled, threshold_level, threshold_type
        )

    def RFmxSpecAn_DPDCfgApplyDPDConfigurationInput(self, vi, selector_string, configuration_input):
        """RFmxSpecAn_DPDCfgApplyDPDConfigurationInput."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput_cfunc is None:
                self.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgApplyDPDConfigurationInput"
                )
                self.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput_cfunc(
            vi, selector_string, configuration_input
        )

    def RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType(
        self, vi, selector_string, lut_correction_type
    ):
        """RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType_cfunc is None:
                self.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType_cfunc = (
                    self._get_library_function("RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType")
                )
                self.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType_cfunc(
            vi, selector_string, lut_correction_type
        )

    def RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType(
        self, vi, selector_string, memory_model_correction_type
    ):
        """RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType_cfunc is None:
                self.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType_cfunc = (
                    self._get_library_function("RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType")
                )
                self.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType_cfunc(
            vi, selector_string, memory_model_correction_type
        )

    def RFmxSpecAn_DPDCfgAveraging(self, vi, selector_string, averaging_enabled, averaging_count):
        """RFmxSpecAn_DPDCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgAveraging_cfunc is None:
                self.RFmxSpecAn_DPDCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgAveraging"
                )
                self.RFmxSpecAn_DPDCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count
        )

    def RFmxSpecAn_DPDCfgDPDModel(self, vi, selector_string, dpd_model):
        """RFmxSpecAn_DPDCfgDPDModel."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgDPDModel_cfunc is None:
                self.RFmxSpecAn_DPDCfgDPDModel_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgDPDModel"
                )
                self.RFmxSpecAn_DPDCfgDPDModel_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgDPDModel_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgDPDModel_cfunc(vi, selector_string, dpd_model)

    def RFmxSpecAn_DPDCfgDUTAverageInputPower(self, vi, selector_string, dut_average_input_power):
        """RFmxSpecAn_DPDCfgDUTAverageInputPower."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgDUTAverageInputPower_cfunc is None:
                self.RFmxSpecAn_DPDCfgDUTAverageInputPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgDUTAverageInputPower"
                )
                self.RFmxSpecAn_DPDCfgDUTAverageInputPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_DPDCfgDUTAverageInputPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgDUTAverageInputPower_cfunc(
            vi, selector_string, dut_average_input_power
        )

    def RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms(
        self,
        vi,
        selector_string,
        memory_polynomial_lead_order,
        memory_polynomial_lag_order,
        memory_polynomial_lead_memory_depth,
        memory_polynomial_lag_memory_depth,
        memory_polynomial_maximum_lead,
        memory_polynomial_maximum_lag,
    ):
        """RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms_cfunc is None:
                self.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms_cfunc = (
                    self._get_library_function(
                        "RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms"
                    )
                )
                self.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms_cfunc(
            vi,
            selector_string,
            memory_polynomial_lead_order,
            memory_polynomial_lag_order,
            memory_polynomial_lead_memory_depth,
            memory_polynomial_lag_memory_depth,
            memory_polynomial_maximum_lead,
            memory_polynomial_maximum_lag,
        )

    def RFmxSpecAn_DPDCfgIterativeDPDEnabled(self, vi, selector_string, iterative_dpd_enabled):
        """RFmxSpecAn_DPDCfgIterativeDPDEnabled."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgIterativeDPDEnabled_cfunc is None:
                self.RFmxSpecAn_DPDCfgIterativeDPDEnabled_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgIterativeDPDEnabled"
                )
                self.RFmxSpecAn_DPDCfgIterativeDPDEnabled_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgIterativeDPDEnabled_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgIterativeDPDEnabled_cfunc(
            vi, selector_string, iterative_dpd_enabled
        )

    def RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit(
        self, vi, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
    ):
        """RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit_cfunc is None:
                self.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit"
                )
                self.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit_cfunc(
            vi, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
        )

    def RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit(
        self, vi, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
    ):
        """RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit_cfunc is None:
                self.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit"
                )
                self.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit_cfunc(
            vi, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
        )

    def RFmxSpecAn_DPDCfgLookupTableStepSize(self, vi, selector_string, step_size):
        """RFmxSpecAn_DPDCfgLookupTableStepSize."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgLookupTableStepSize_cfunc is None:
                self.RFmxSpecAn_DPDCfgLookupTableStepSize_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgLookupTableStepSize"
                )
                self.RFmxSpecAn_DPDCfgLookupTableStepSize_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_DPDCfgLookupTableStepSize_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgLookupTableStepSize_cfunc(vi, selector_string, step_size)

    def RFmxSpecAn_DPDCfgLookupTableThreshold(
        self, vi, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """RFmxSpecAn_DPDCfgLookupTableThreshold."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgLookupTableThreshold_cfunc is None:
                self.RFmxSpecAn_DPDCfgLookupTableThreshold_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgLookupTableThreshold"
                )
                self.RFmxSpecAn_DPDCfgLookupTableThreshold_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgLookupTableThreshold_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgLookupTableThreshold_cfunc(
            vi, selector_string, threshold_enabled, threshold_level, threshold_type
        )

    def RFmxSpecAn_DPDCfgLookupTableType(self, vi, selector_string, lookup_table_type):
        """RFmxSpecAn_DPDCfgLookupTableType."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgLookupTableType_cfunc is None:
                self.RFmxSpecAn_DPDCfgLookupTableType_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgLookupTableType"
                )
                self.RFmxSpecAn_DPDCfgLookupTableType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgLookupTableType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgLookupTableType_cfunc(vi, selector_string, lookup_table_type)

    def RFmxSpecAn_DPDCfgMeasurementInterval(self, vi, selector_string, measurement_interval):
        """RFmxSpecAn_DPDCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_DPDCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgMeasurementInterval"
                )
                self.RFmxSpecAn_DPDCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_DPDCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_DPDCfgMeasurementSampleRate(
        self, vi, selector_string, sample_rate_mode, sample_rate
    ):
        """RFmxSpecAn_DPDCfgMeasurementSampleRate."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgMeasurementSampleRate_cfunc is None:
                self.RFmxSpecAn_DPDCfgMeasurementSampleRate_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgMeasurementSampleRate"
                )
                self.RFmxSpecAn_DPDCfgMeasurementSampleRate_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_DPDCfgMeasurementSampleRate_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgMeasurementSampleRate_cfunc(
            vi, selector_string, sample_rate_mode, sample_rate
        )

    def RFmxSpecAn_DPDCfgMemoryPolynomial(
        self, vi, selector_string, memory_polynomial_order, memory_polynomial_memory_depth
    ):
        """RFmxSpecAn_DPDCfgMemoryPolynomial."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgMemoryPolynomial_cfunc is None:
                self.RFmxSpecAn_DPDCfgMemoryPolynomial_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgMemoryPolynomial"
                )
                self.RFmxSpecAn_DPDCfgMemoryPolynomial_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgMemoryPolynomial_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgMemoryPolynomial_cfunc(
            vi, selector_string, memory_polynomial_order, memory_polynomial_memory_depth
        )

    def RFmxSpecAn_DPDCfgSynchronizationMethod(self, vi, selector_string, synchronization_method):
        """RFmxSpecAn_DPDCfgSynchronizationMethod."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDCfgSynchronizationMethod_cfunc is None:
                self.RFmxSpecAn_DPDCfgSynchronizationMethod_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDCfgSynchronizationMethod"
                )
                self.RFmxSpecAn_DPDCfgSynchronizationMethod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_DPDCfgSynchronizationMethod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDCfgSynchronizationMethod_cfunc(
            vi, selector_string, synchronization_method
        )

    def RFmxSpecAn_ACPCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_ACPCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgAveraging_cfunc is None:
                self.RFmxSpecAn_ACPCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgAveraging"
                )
                self.RFmxSpecAn_ACPCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth(
        self, vi, selector_string, integration_bandwidth
    ):
        """RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth_cfunc is None:
                self.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth_cfunc = (
                    self._get_library_function("RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth")
                )
                self.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth_cfunc(
            vi, selector_string, integration_bandwidth
        )

    def RFmxSpecAn_ACPCfgCarrierMode(self, vi, selector_string, carrier_mode):
        """RFmxSpecAn_ACPCfgCarrierMode."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgCarrierMode_cfunc is None:
                self.RFmxSpecAn_ACPCfgCarrierMode_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgCarrierMode"
                )
                self.RFmxSpecAn_ACPCfgCarrierMode_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgCarrierMode_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgCarrierMode_cfunc(vi, selector_string, carrier_mode)

    def RFmxSpecAn_ACPCfgCarrierFrequency(self, vi, selector_string, carrier_frequency):
        """RFmxSpecAn_ACPCfgCarrierFrequency."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgCarrierFrequency_cfunc is None:
                self.RFmxSpecAn_ACPCfgCarrierFrequency_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgCarrierFrequency"
                )
                self.RFmxSpecAn_ACPCfgCarrierFrequency_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgCarrierFrequency_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgCarrierFrequency_cfunc(vi, selector_string, carrier_frequency)

    def RFmxSpecAn_ACPCfgCarrierRRCFilter(self, vi, selector_string, rrc_filter_enabled, rrc_alpha):
        """RFmxSpecAn_ACPCfgCarrierRRCFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgCarrierRRCFilter_cfunc is None:
                self.RFmxSpecAn_ACPCfgCarrierRRCFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgCarrierRRCFilter"
                )
                self.RFmxSpecAn_ACPCfgCarrierRRCFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgCarrierRRCFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgCarrierRRCFilter_cfunc(
            vi, selector_string, rrc_filter_enabled, rrc_alpha
        )

    def RFmxSpecAn_ACPCfgFFT(self, vi, selector_string, fft_window, fft_padding):
        """RFmxSpecAn_ACPCfgFFT."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgFFT_cfunc is None:
                self.RFmxSpecAn_ACPCfgFFT_cfunc = self._get_library_function("RFmxSpecAn_ACPCfgFFT")
                self.RFmxSpecAn_ACPCfgFFT_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgFFT_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgFFT_cfunc(vi, selector_string, fft_window, fft_padding)

    def RFmxSpecAn_ACPCfgMeasurementMethod(self, vi, selector_string, measurement_method):
        """RFmxSpecAn_ACPCfgMeasurementMethod."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgMeasurementMethod_cfunc is None:
                self.RFmxSpecAn_ACPCfgMeasurementMethod_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgMeasurementMethod"
                )
                self.RFmxSpecAn_ACPCfgMeasurementMethod_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgMeasurementMethod_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgMeasurementMethod_cfunc(
            vi, selector_string, measurement_method
        )

    def RFmxSpecAn_ACPCfgNoiseCompensationEnabled(
        self, vi, selector_string, noise_compensation_enabled
    ):
        """RFmxSpecAn_ACPCfgNoiseCompensationEnabled."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgNoiseCompensationEnabled_cfunc is None:
                self.RFmxSpecAn_ACPCfgNoiseCompensationEnabled_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgNoiseCompensationEnabled"
                )
                self.RFmxSpecAn_ACPCfgNoiseCompensationEnabled_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgNoiseCompensationEnabled_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgNoiseCompensationEnabled_cfunc(
            vi, selector_string, noise_compensation_enabled
        )

    def RFmxSpecAn_ACPCfgNumberOfCarriers(self, vi, selector_string, number_of_carriers):
        """RFmxSpecAn_ACPCfgNumberOfCarriers."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgNumberOfCarriers_cfunc is None:
                self.RFmxSpecAn_ACPCfgNumberOfCarriers_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgNumberOfCarriers"
                )
                self.RFmxSpecAn_ACPCfgNumberOfCarriers_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgNumberOfCarriers_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgNumberOfCarriers_cfunc(vi, selector_string, number_of_carriers)

    def RFmxSpecAn_ACPCfgNumberOfOffsets(self, vi, selector_string, number_of_offsets):
        """RFmxSpecAn_ACPCfgNumberOfOffsets."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgNumberOfOffsets_cfunc is None:
                self.RFmxSpecAn_ACPCfgNumberOfOffsets_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgNumberOfOffsets"
                )
                self.RFmxSpecAn_ACPCfgNumberOfOffsets_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgNumberOfOffsets_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgNumberOfOffsets_cfunc(vi, selector_string, number_of_offsets)

    def RFmxSpecAn_ACPCfgOffsetArray(
        self,
        vi,
        selector_string,
        offset_frequency,
        offset_sideband,
        offset_enabled,
        number_of_elements,
    ):
        """RFmxSpecAn_ACPCfgOffsetArray."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetArray_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetArray"
                )
                self.RFmxSpecAn_ACPCfgOffsetArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetArray_cfunc(
            vi,
            selector_string,
            offset_frequency,
            offset_sideband,
            offset_enabled,
            number_of_elements,
        )

    def RFmxSpecAn_ACPCfgOffsetFrequencyDefinition(
        self, vi, selector_string, offset_frequency_definition
    ):
        """RFmxSpecAn_ACPCfgOffsetFrequencyDefinition."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetFrequencyDefinition"
                )
                self.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition_cfunc(
            vi, selector_string, offset_frequency_definition
        )

    def RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray(
        self, vi, selector_string, integration_bandwidth, number_of_elements
    ):
        """RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray")
                )
                self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray_cfunc(
            vi, selector_string, integration_bandwidth, number_of_elements
        )

    def RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth(
        self, vi, selector_string, integration_bandwidth
    ):
        """RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth"
                )
                self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth_cfunc(
            vi, selector_string, integration_bandwidth
        )

    def RFmxSpecAn_ACPCfgOffsetPowerReferenceArray(
        self,
        vi,
        selector_string,
        offset_power_reference_carrier,
        offset_power_reference_specific,
        number_of_elements,
    ):
        """RFmxSpecAn_ACPCfgOffsetPowerReferenceArray."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetPowerReferenceArray"
                )
                self.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray_cfunc(
            vi,
            selector_string,
            offset_power_reference_carrier,
            offset_power_reference_specific,
            number_of_elements,
        )

    def RFmxSpecAn_ACPCfgOffsetPowerReference(
        self, vi, selector_string, offset_reference_carrier, offset_reference_specific
    ):
        """RFmxSpecAn_ACPCfgOffsetPowerReference."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetPowerReference_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetPowerReference_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetPowerReference"
                )
                self.RFmxSpecAn_ACPCfgOffsetPowerReference_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetPowerReference_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetPowerReference_cfunc(
            vi, selector_string, offset_reference_carrier, offset_reference_specific
        )

    def RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray(
        self, vi, selector_string, relative_attenuation, number_of_elements
    ):
        """RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray")
                )
                self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray_cfunc(
            vi, selector_string, relative_attenuation, number_of_elements
        )

    def RFmxSpecAn_ACPCfgOffsetRelativeAttenuation(self, vi, selector_string, relative_attenuation):
        """RFmxSpecAn_ACPCfgOffsetRelativeAttenuation."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetRelativeAttenuation"
                )
                self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation_cfunc(
            vi, selector_string, relative_attenuation
        )

    def RFmxSpecAn_ACPCfgOffsetRRCFilterArray(
        self, vi, selector_string, rrc_filter_enabled, rrc_alpha, number_of_elements
    ):
        """RFmxSpecAn_ACPCfgOffsetRRCFilterArray."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetRRCFilterArray_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetRRCFilterArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetRRCFilterArray"
                )
                self.RFmxSpecAn_ACPCfgOffsetRRCFilterArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffsetRRCFilterArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetRRCFilterArray_cfunc(
            vi, selector_string, rrc_filter_enabled, rrc_alpha, number_of_elements
        )

    def RFmxSpecAn_ACPCfgOffsetRRCFilter(self, vi, selector_string, rrc_filter_enabled, rrc_alpha):
        """RFmxSpecAn_ACPCfgOffsetRRCFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffsetRRCFilter_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffsetRRCFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffsetRRCFilter"
                )
                self.RFmxSpecAn_ACPCfgOffsetRRCFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgOffsetRRCFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffsetRRCFilter_cfunc(
            vi, selector_string, rrc_filter_enabled, rrc_alpha
        )

    def RFmxSpecAn_ACPCfgOffset(
        self, vi, selector_string, offset_frequency, offset_sideband, offset_enabled
    ):
        """RFmxSpecAn_ACPCfgOffset."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgOffset_cfunc is None:
                self.RFmxSpecAn_ACPCfgOffset_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgOffset"
                )
                self.RFmxSpecAn_ACPCfgOffset_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgOffset_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgOffset_cfunc(
            vi, selector_string, offset_frequency, offset_sideband, offset_enabled
        )

    def RFmxSpecAn_ACPCfgPowerUnits(self, vi, selector_string, power_units):
        """RFmxSpecAn_ACPCfgPowerUnits."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgPowerUnits_cfunc is None:
                self.RFmxSpecAn_ACPCfgPowerUnits_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgPowerUnits"
                )
                self.RFmxSpecAn_ACPCfgPowerUnits_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgPowerUnits_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgPowerUnits_cfunc(vi, selector_string, power_units)

    def RFmxSpecAn_ACPCfgRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_ACPCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_ACPCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgRBWFilter"
                )
                self.RFmxSpecAn_ACPCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_ACPCfgSweepTime(self, vi, selector_string, sweep_time_auto, sweep_time_interval):
        """RFmxSpecAn_ACPCfgSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgSweepTime_cfunc is None:
                self.RFmxSpecAn_ACPCfgSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgSweepTime"
                )
                self.RFmxSpecAn_ACPCfgSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_ACPCfgSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_ACPCfgDetector(self, vi, selector_string, detector_type, detector_points):
        """RFmxSpecAn_ACPCfgDetector."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPCfgDetector_cfunc is None:
                self.RFmxSpecAn_ACPCfgDetector_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPCfgDetector"
                )
                self.RFmxSpecAn_ACPCfgDetector_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_ACPCfgDetector_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPCfgDetector_cfunc(
            vi, selector_string, detector_type, detector_points
        )

    def RFmxSpecAn_CCDFCfgMeasurementInterval(self, vi, selector_string, measurement_interval):
        """RFmxSpecAn_CCDFCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_CCDFCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFCfgMeasurementInterval"
                )
                self.RFmxSpecAn_CCDFCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CCDFCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_CCDFCfgNumberOfRecords(self, vi, selector_string, number_of_records):
        """RFmxSpecAn_CCDFCfgNumberOfRecords."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFCfgNumberOfRecords_cfunc is None:
                self.RFmxSpecAn_CCDFCfgNumberOfRecords_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFCfgNumberOfRecords"
                )
                self.RFmxSpecAn_CCDFCfgNumberOfRecords_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CCDFCfgNumberOfRecords_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFCfgNumberOfRecords_cfunc(vi, selector_string, number_of_records)

    def RFmxSpecAn_CCDFCfgRBWFilter(self, vi, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """RFmxSpecAn_CCDFCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_CCDFCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFCfgRBWFilter"
                )
                self.RFmxSpecAn_CCDFCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CCDFCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFCfgRBWFilter_cfunc(
            vi, selector_string, rbw, rbw_filter_type, rrc_alpha
        )

    def RFmxSpecAn_CCDFCfgThreshold(
        self, vi, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """RFmxSpecAn_CCDFCfgThreshold."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFCfgThreshold_cfunc is None:
                self.RFmxSpecAn_CCDFCfgThreshold_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFCfgThreshold"
                )
                self.RFmxSpecAn_CCDFCfgThreshold_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CCDFCfgThreshold_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFCfgThreshold_cfunc(
            vi, selector_string, threshold_enabled, threshold_level, threshold_type
        )

    def RFmxSpecAn_CHPCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_CHPCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgAveraging_cfunc is None:
                self.RFmxSpecAn_CHPCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgAveraging"
                )
                self.RFmxSpecAn_CHPCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CHPCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_CHPCfgCarrierOffset(self, vi, selector_string, carrier_frequency):
        """RFmxSpecAn_CHPCfgCarrierOffset."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgCarrierOffset_cfunc is None:
                self.RFmxSpecAn_CHPCfgCarrierOffset_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgCarrierOffset"
                )
                self.RFmxSpecAn_CHPCfgCarrierOffset_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CHPCfgCarrierOffset_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgCarrierOffset_cfunc(vi, selector_string, carrier_frequency)

    def RFmxSpecAn_CHPCfgFFT(self, vi, selector_string, fft_window, fft_padding):
        """RFmxSpecAn_CHPCfgFFT."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgFFT_cfunc is None:
                self.RFmxSpecAn_CHPCfgFFT_cfunc = self._get_library_function("RFmxSpecAn_CHPCfgFFT")
                self.RFmxSpecAn_CHPCfgFFT_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CHPCfgFFT_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgFFT_cfunc(vi, selector_string, fft_window, fft_padding)

    def RFmxSpecAn_CHPCfgIntegrationBandwidth(self, vi, selector_string, integration_bandwidth):
        """RFmxSpecAn_CHPCfgIntegrationBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgIntegrationBandwidth_cfunc is None:
                self.RFmxSpecAn_CHPCfgIntegrationBandwidth_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgIntegrationBandwidth"
                )
                self.RFmxSpecAn_CHPCfgIntegrationBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CHPCfgIntegrationBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgIntegrationBandwidth_cfunc(
            vi, selector_string, integration_bandwidth
        )

    def RFmxSpecAn_CHPCfgNumberOfCarriers(self, vi, selector_string, number_of_carriers):
        """RFmxSpecAn_CHPCfgNumberOfCarriers."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgNumberOfCarriers_cfunc is None:
                self.RFmxSpecAn_CHPCfgNumberOfCarriers_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgNumberOfCarriers"
                )
                self.RFmxSpecAn_CHPCfgNumberOfCarriers_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CHPCfgNumberOfCarriers_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgNumberOfCarriers_cfunc(vi, selector_string, number_of_carriers)

    def RFmxSpecAn_CHPCfgRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_CHPCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_CHPCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgRBWFilter"
                )
                self.RFmxSpecAn_CHPCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CHPCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_CHPCfgRRCFilter(self, vi, selector_string, rrc_filter_enabled, rrc_alpha):
        """RFmxSpecAn_CHPCfgRRCFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgRRCFilter_cfunc is None:
                self.RFmxSpecAn_CHPCfgRRCFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgRRCFilter"
                )
                self.RFmxSpecAn_CHPCfgRRCFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CHPCfgRRCFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgRRCFilter_cfunc(
            vi, selector_string, rrc_filter_enabled, rrc_alpha
        )

    def RFmxSpecAn_CHPCfgSpan(self, vi, selector_string, span):
        """RFmxSpecAn_CHPCfgSpan."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgSpan_cfunc is None:
                self.RFmxSpecAn_CHPCfgSpan_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgSpan"
                )
                self.RFmxSpecAn_CHPCfgSpan_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CHPCfgSpan_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgSpan_cfunc(vi, selector_string, span)

    def RFmxSpecAn_CHPCfgSweepTime(self, vi, selector_string, sweep_time_auto, sweep_time_interval):
        """RFmxSpecAn_CHPCfgSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgSweepTime_cfunc is None:
                self.RFmxSpecAn_CHPCfgSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgSweepTime"
                )
                self.RFmxSpecAn_CHPCfgSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CHPCfgSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_CHPCfgDetector(self, vi, selector_string, detector_type, detector_points):
        """RFmxSpecAn_CHPCfgDetector."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPCfgDetector_cfunc is None:
                self.RFmxSpecAn_CHPCfgDetector_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPCfgDetector"
                )
                self.RFmxSpecAn_CHPCfgDetector_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_CHPCfgDetector_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPCfgDetector_cfunc(
            vi, selector_string, detector_type, detector_points
        )

    def RFmxSpecAn_HarmCfgAutoHarmonics(self, vi, selector_string, auto_harmonics_setup_enabled):
        """RFmxSpecAn_HarmCfgAutoHarmonics."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgAutoHarmonics_cfunc is None:
                self.RFmxSpecAn_HarmCfgAutoHarmonics_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmCfgAutoHarmonics"
                )
                self.RFmxSpecAn_HarmCfgAutoHarmonics_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_HarmCfgAutoHarmonics_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgAutoHarmonics_cfunc(
            vi, selector_string, auto_harmonics_setup_enabled
        )

    def RFmxSpecAn_HarmCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_HarmCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgAveraging_cfunc is None:
                self.RFmxSpecAn_HarmCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmCfgAveraging"
                )
                self.RFmxSpecAn_HarmCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_HarmCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_HarmCfgFundamentalMeasurementInterval(
        self, vi, selector_string, measurement_interval
    ):
        """RFmxSpecAn_HarmCfgFundamentalMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval_cfunc = (
                    self._get_library_function("RFmxSpecAn_HarmCfgFundamentalMeasurementInterval")
                )
                self.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_HarmCfgFundamentalRBW(
        self, vi, selector_string, rbw, rbw_filter_type, rrc_alpha
    ):
        """RFmxSpecAn_HarmCfgFundamentalRBW."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgFundamentalRBW_cfunc is None:
                self.RFmxSpecAn_HarmCfgFundamentalRBW_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmCfgFundamentalRBW"
                )
                self.RFmxSpecAn_HarmCfgFundamentalRBW_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_HarmCfgFundamentalRBW_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgFundamentalRBW_cfunc(
            vi, selector_string, rbw, rbw_filter_type, rrc_alpha
        )

    def RFmxSpecAn_HarmCfgHarmonicArray(
        self,
        vi,
        selector_string,
        harmonic_order,
        harmonic_bandwidth,
        harmonic_enabled,
        harmonic_measurement_interval,
        number_of_elements,
    ):
        """RFmxSpecAn_HarmCfgHarmonicArray."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgHarmonicArray_cfunc is None:
                self.RFmxSpecAn_HarmCfgHarmonicArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmCfgHarmonicArray"
                )
                self.RFmxSpecAn_HarmCfgHarmonicArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_HarmCfgHarmonicArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgHarmonicArray_cfunc(
            vi,
            selector_string,
            harmonic_order,
            harmonic_bandwidth,
            harmonic_enabled,
            harmonic_measurement_interval,
            number_of_elements,
        )

    def RFmxSpecAn_HarmCfgHarmonic(
        self,
        vi,
        selector_string,
        harmonic_order,
        harmonic_bandwidth,
        harmonic_enabled,
        harmonic_measurement_interval,
    ):
        """RFmxSpecAn_HarmCfgHarmonic."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgHarmonic_cfunc is None:
                self.RFmxSpecAn_HarmCfgHarmonic_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmCfgHarmonic"
                )
                self.RFmxSpecAn_HarmCfgHarmonic_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_HarmCfgHarmonic_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgHarmonic_cfunc(
            vi,
            selector_string,
            harmonic_order,
            harmonic_bandwidth,
            harmonic_enabled,
            harmonic_measurement_interval,
        )

    def RFmxSpecAn_HarmCfgNumberOfHarmonics(self, vi, selector_string, number_of_harmonics):
        """RFmxSpecAn_HarmCfgNumberOfHarmonics."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmCfgNumberOfHarmonics_cfunc is None:
                self.RFmxSpecAn_HarmCfgNumberOfHarmonics_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmCfgNumberOfHarmonics"
                )
                self.RFmxSpecAn_HarmCfgNumberOfHarmonics_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_HarmCfgNumberOfHarmonics_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmCfgNumberOfHarmonics_cfunc(
            vi, selector_string, number_of_harmonics
        )

    def RFmxSpecAn_SEMCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_SEMCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgAveraging_cfunc is None:
                self.RFmxSpecAn_SEMCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgAveraging"
                )
                self.RFmxSpecAn_SEMCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_SEMCfgCarrierChannelBandwidth(
        self, vi, selector_string, carrier_channel_bandwidth
    ):
        """RFmxSpecAn_SEMCfgCarrierChannelBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgCarrierChannelBandwidth_cfunc is None:
                self.RFmxSpecAn_SEMCfgCarrierChannelBandwidth_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgCarrierChannelBandwidth"
                )
                self.RFmxSpecAn_SEMCfgCarrierChannelBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgCarrierChannelBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgCarrierChannelBandwidth_cfunc(
            vi, selector_string, carrier_channel_bandwidth
        )

    def RFmxSpecAn_SEMCfgCarrierEnabled(self, vi, selector_string, carrier_enabled):
        """RFmxSpecAn_SEMCfgCarrierEnabled."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgCarrierEnabled_cfunc is None:
                self.RFmxSpecAn_SEMCfgCarrierEnabled_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgCarrierEnabled"
                )
                self.RFmxSpecAn_SEMCfgCarrierEnabled_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgCarrierEnabled_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgCarrierEnabled_cfunc(vi, selector_string, carrier_enabled)

    def RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth(
        self, vi, selector_string, integration_bandwidth
    ):
        """RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth_cfunc is None:
                self.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth_cfunc = (
                    self._get_library_function("RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth")
                )
                self.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth_cfunc(
            vi, selector_string, integration_bandwidth
        )

    def RFmxSpecAn_SEMCfgCarrierFrequency(self, vi, selector_string, carrier_frequency):
        """RFmxSpecAn_SEMCfgCarrierFrequency."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgCarrierFrequency_cfunc is None:
                self.RFmxSpecAn_SEMCfgCarrierFrequency_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgCarrierFrequency"
                )
                self.RFmxSpecAn_SEMCfgCarrierFrequency_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgCarrierFrequency_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgCarrierFrequency_cfunc(vi, selector_string, carrier_frequency)

    def RFmxSpecAn_SEMCfgCarrierRBWFilter(
        self, vi, selector_string, rbw_auto, rbw, rbw_filter_type
    ):
        """RFmxSpecAn_SEMCfgCarrierRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgCarrierRBWFilter_cfunc is None:
                self.RFmxSpecAn_SEMCfgCarrierRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgCarrierRBWFilter"
                )
                self.RFmxSpecAn_SEMCfgCarrierRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgCarrierRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgCarrierRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_SEMCfgCarrierRRCFilter(self, vi, selector_string, rrc_filter_enabled, rrc_alpha):
        """RFmxSpecAn_SEMCfgCarrierRRCFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgCarrierRRCFilter_cfunc is None:
                self.RFmxSpecAn_SEMCfgCarrierRRCFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgCarrierRRCFilter"
                )
                self.RFmxSpecAn_SEMCfgCarrierRRCFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgCarrierRRCFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgCarrierRRCFilter_cfunc(
            vi, selector_string, rrc_filter_enabled, rrc_alpha
        )

    def RFmxSpecAn_SEMCfgFFT(self, vi, selector_string, fft_window, fft_padding):
        """RFmxSpecAn_SEMCfgFFT."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgFFT_cfunc is None:
                self.RFmxSpecAn_SEMCfgFFT_cfunc = self._get_library_function("RFmxSpecAn_SEMCfgFFT")
                self.RFmxSpecAn_SEMCfgFFT_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgFFT_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgFFT_cfunc(vi, selector_string, fft_window, fft_padding)

    def RFmxSpecAn_SEMCfgNumberOfCarriers(self, vi, selector_string, number_of_carriers):
        """RFmxSpecAn_SEMCfgNumberOfCarriers."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgNumberOfCarriers_cfunc is None:
                self.RFmxSpecAn_SEMCfgNumberOfCarriers_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgNumberOfCarriers"
                )
                self.RFmxSpecAn_SEMCfgNumberOfCarriers_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgNumberOfCarriers_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgNumberOfCarriers_cfunc(vi, selector_string, number_of_carriers)

    def RFmxSpecAn_SEMCfgNumberOfOffsets(self, vi, selector_string, number_of_offsets):
        """RFmxSpecAn_SEMCfgNumberOfOffsets."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgNumberOfOffsets_cfunc is None:
                self.RFmxSpecAn_SEMCfgNumberOfOffsets_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgNumberOfOffsets"
                )
                self.RFmxSpecAn_SEMCfgNumberOfOffsets_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgNumberOfOffsets_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgNumberOfOffsets_cfunc(vi, selector_string, number_of_offsets)

    def RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray(
        self,
        vi,
        selector_string,
        absolute_limit_mode,
        absolute_limit_start,
        absolute_limit_stop,
        number_of_elements,
    ):
        """RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray"
                )
                self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray_cfunc(
            vi,
            selector_string,
            absolute_limit_mode,
            absolute_limit_start,
            absolute_limit_stop,
            number_of_elements,
        )

    def RFmxSpecAn_SEMCfgOffsetAbsoluteLimit(
        self, vi, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        """RFmxSpecAn_SEMCfgOffsetAbsoluteLimit."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetAbsoluteLimit"
                )
                self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit_cfunc(
            vi, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
        )

    def RFmxSpecAn_SEMCfgOffsetBandwidthIntegral(self, vi, selector_string, bandwidth_integral):
        """RFmxSpecAn_SEMCfgOffsetBandwidthIntegral."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetBandwidthIntegral"
                )
                self.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral_cfunc(
            vi, selector_string, bandwidth_integral
        )

    def RFmxSpecAn_SEMCfgOffsetFrequencyArray(
        self,
        vi,
        selector_string,
        offset_start_frequency,
        offset_stop_frequency,
        offset_enabled,
        offset_sideband,
        number_of_elements,
    ):
        """RFmxSpecAn_SEMCfgOffsetFrequencyArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetFrequencyArray_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetFrequencyArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetFrequencyArray"
                )
                self.RFmxSpecAn_SEMCfgOffsetFrequencyArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetFrequencyArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetFrequencyArray_cfunc(
            vi,
            selector_string,
            offset_start_frequency,
            offset_stop_frequency,
            offset_enabled,
            offset_sideband,
            number_of_elements,
        )

    def RFmxSpecAn_SEMCfgOffsetFrequencyDefinition(
        self, vi, selector_string, offset_frequency_definition
    ):
        """RFmxSpecAn_SEMCfgOffsetFrequencyDefinition."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetFrequencyDefinition"
                )
                self.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition_cfunc(
            vi, selector_string, offset_frequency_definition
        )

    def RFmxSpecAn_SEMCfgOffsetFrequency(
        self,
        vi,
        selector_string,
        offset_start_frequency,
        offset_stop_frequency,
        offset_enabled,
        offset_sideband,
    ):
        """RFmxSpecAn_SEMCfgOffsetFrequency."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetFrequency_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetFrequency_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetFrequency"
                )
                self.RFmxSpecAn_SEMCfgOffsetFrequency_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetFrequency_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetFrequency_cfunc(
            vi,
            selector_string,
            offset_start_frequency,
            offset_stop_frequency,
            offset_enabled,
            offset_sideband,
        )

    def RFmxSpecAn_SEMCfgOffsetLimitFailMask(self, vi, selector_string, limit_fail_mask):
        """RFmxSpecAn_SEMCfgOffsetLimitFailMask."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetLimitFailMask_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetLimitFailMask_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetLimitFailMask"
                )
                self.RFmxSpecAn_SEMCfgOffsetLimitFailMask_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetLimitFailMask_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetLimitFailMask_cfunc(vi, selector_string, limit_fail_mask)

    def RFmxSpecAn_SEMCfgOffsetRBWFilterArray(
        self, vi, selector_string, rbw_auto, rbw, rbw_filter_type, number_of_elements
    ):
        """RFmxSpecAn_SEMCfgOffsetRBWFilterArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetRBWFilterArray_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetRBWFilterArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetRBWFilterArray"
                )
                self.RFmxSpecAn_SEMCfgOffsetRBWFilterArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetRBWFilterArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetRBWFilterArray_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type, number_of_elements
        )

    def RFmxSpecAn_SEMCfgOffsetRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_SEMCfgOffsetRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetRBWFilter_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetRBWFilter"
                )
                self.RFmxSpecAn_SEMCfgOffsetRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray(
        self, vi, selector_string, relative_attenuation, number_of_elements
    ):
        """RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray")
                )
                self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray_cfunc(
            vi, selector_string, relative_attenuation, number_of_elements
        )

    def RFmxSpecAn_SEMCfgOffsetRelativeAttenuation(self, vi, selector_string, relative_attenuation):
        """RFmxSpecAn_SEMCfgOffsetRelativeAttenuation."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetRelativeAttenuation"
                )
                self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation_cfunc(
            vi, selector_string, relative_attenuation
        )

    def RFmxSpecAn_SEMCfgOffsetRelativeLimitArray(
        self,
        vi,
        selector_string,
        relative_limit_mode,
        relative_limit_start,
        relative_limit_stop,
        number_of_elements,
    ):
        """RFmxSpecAn_SEMCfgOffsetRelativeLimitArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetRelativeLimitArray"
                )
                self.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray_cfunc(
            vi,
            selector_string,
            relative_limit_mode,
            relative_limit_start,
            relative_limit_stop,
            number_of_elements,
        )

    def RFmxSpecAn_SEMCfgOffsetRelativeLimit(
        self, vi, selector_string, relative_limit_mode, relative_limit_start, relative_limit_stop
    ):
        """RFmxSpecAn_SEMCfgOffsetRelativeLimit."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgOffsetRelativeLimit_cfunc is None:
                self.RFmxSpecAn_SEMCfgOffsetRelativeLimit_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgOffsetRelativeLimit"
                )
                self.RFmxSpecAn_SEMCfgOffsetRelativeLimit_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgOffsetRelativeLimit_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgOffsetRelativeLimit_cfunc(
            vi, selector_string, relative_limit_mode, relative_limit_start, relative_limit_stop
        )

    def RFmxSpecAn_SEMCfgPowerUnits(self, vi, selector_string, power_units):
        """RFmxSpecAn_SEMCfgPowerUnits."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgPowerUnits_cfunc is None:
                self.RFmxSpecAn_SEMCfgPowerUnits_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgPowerUnits"
                )
                self.RFmxSpecAn_SEMCfgPowerUnits_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgPowerUnits_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgPowerUnits_cfunc(vi, selector_string, power_units)

    def RFmxSpecAn_SEMCfgReferenceType(self, vi, selector_string, reference_type):
        """RFmxSpecAn_SEMCfgReferenceType."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgReferenceType_cfunc is None:
                self.RFmxSpecAn_SEMCfgReferenceType_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgReferenceType"
                )
                self.RFmxSpecAn_SEMCfgReferenceType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_SEMCfgReferenceType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgReferenceType_cfunc(vi, selector_string, reference_type)

    def RFmxSpecAn_SEMCfgSweepTime(self, vi, selector_string, sweep_time_auto, sweep_time_interval):
        """RFmxSpecAn_SEMCfgSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMCfgSweepTime_cfunc is None:
                self.RFmxSpecAn_SEMCfgSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMCfgSweepTime"
                )
                self.RFmxSpecAn_SEMCfgSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_SEMCfgSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMCfgSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_OBWCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_OBWCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgAveraging_cfunc is None:
                self.RFmxSpecAn_OBWCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWCfgAveraging"
                )
                self.RFmxSpecAn_OBWCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_OBWCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_OBWCfgBandwidthPercentage(self, vi, selector_string, bandwidth_percentage):
        """RFmxSpecAn_OBWCfgBandwidthPercentage."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgBandwidthPercentage_cfunc is None:
                self.RFmxSpecAn_OBWCfgBandwidthPercentage_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWCfgBandwidthPercentage"
                )
                self.RFmxSpecAn_OBWCfgBandwidthPercentage_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_OBWCfgBandwidthPercentage_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgBandwidthPercentage_cfunc(
            vi, selector_string, bandwidth_percentage
        )

    def RFmxSpecAn_OBWCfgFFT(self, vi, selector_string, fft_window, fft_padding):
        """RFmxSpecAn_OBWCfgFFT."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgFFT_cfunc is None:
                self.RFmxSpecAn_OBWCfgFFT_cfunc = self._get_library_function("RFmxSpecAn_OBWCfgFFT")
                self.RFmxSpecAn_OBWCfgFFT_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_OBWCfgFFT_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgFFT_cfunc(vi, selector_string, fft_window, fft_padding)

    def RFmxSpecAn_OBWCfgPowerUnits(self, vi, selector_string, power_units):
        """RFmxSpecAn_OBWCfgPowerUnits."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgPowerUnits_cfunc is None:
                self.RFmxSpecAn_OBWCfgPowerUnits_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWCfgPowerUnits"
                )
                self.RFmxSpecAn_OBWCfgPowerUnits_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_OBWCfgPowerUnits_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgPowerUnits_cfunc(vi, selector_string, power_units)

    def RFmxSpecAn_OBWCfgRBWFilter(self, vi, selector_string, rbw_auto, rbw, rbw_filter_type):
        """RFmxSpecAn_OBWCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_OBWCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWCfgRBWFilter"
                )
                self.RFmxSpecAn_OBWCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_OBWCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgRBWFilter_cfunc(
            vi, selector_string, rbw_auto, rbw, rbw_filter_type
        )

    def RFmxSpecAn_OBWCfgSpan(self, vi, selector_string, span):
        """RFmxSpecAn_OBWCfgSpan."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgSpan_cfunc is None:
                self.RFmxSpecAn_OBWCfgSpan_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWCfgSpan"
                )
                self.RFmxSpecAn_OBWCfgSpan_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_OBWCfgSpan_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgSpan_cfunc(vi, selector_string, span)

    def RFmxSpecAn_OBWCfgSweepTime(self, vi, selector_string, sweep_time_auto, sweep_time_interval):
        """RFmxSpecAn_OBWCfgSweepTime."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWCfgSweepTime_cfunc is None:
                self.RFmxSpecAn_OBWCfgSweepTime_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWCfgSweepTime"
                )
                self.RFmxSpecAn_OBWCfgSweepTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_OBWCfgSweepTime_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWCfgSweepTime_cfunc(
            vi, selector_string, sweep_time_auto, sweep_time_interval
        )

    def RFmxSpecAn_TXPCfgAveraging(
        self, vi, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """RFmxSpecAn_TXPCfgAveraging."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPCfgAveraging_cfunc is None:
                self.RFmxSpecAn_TXPCfgAveraging_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPCfgAveraging"
                )
                self.RFmxSpecAn_TXPCfgAveraging_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_TXPCfgAveraging_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPCfgAveraging_cfunc(
            vi, selector_string, averaging_enabled, averaging_count, averaging_type
        )

    def RFmxSpecAn_TXPCfgMeasurementInterval(self, vi, selector_string, measurement_interval):
        """RFmxSpecAn_TXPCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_TXPCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPCfgMeasurementInterval"
                )
                self.RFmxSpecAn_TXPCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_TXPCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_interval
        )

    def RFmxSpecAn_TXPCfgRBWFilter(self, vi, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """RFmxSpecAn_TXPCfgRBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPCfgRBWFilter_cfunc is None:
                self.RFmxSpecAn_TXPCfgRBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPCfgRBWFilter"
                )
                self.RFmxSpecAn_TXPCfgRBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_TXPCfgRBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPCfgRBWFilter_cfunc(
            vi, selector_string, rbw, rbw_filter_type, rrc_alpha
        )

    def RFmxSpecAn_TXPCfgThreshold(
        self, vi, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """RFmxSpecAn_TXPCfgThreshold."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPCfgThreshold_cfunc is None:
                self.RFmxSpecAn_TXPCfgThreshold_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPCfgThreshold"
                )
                self.RFmxSpecAn_TXPCfgThreshold_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_TXPCfgThreshold_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPCfgThreshold_cfunc(
            vi, selector_string, threshold_enabled, threshold_level, threshold_type
        )

    def RFmxSpecAn_TXPCfgVBWFilter(self, vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        """RFmxSpecAn_TXPCfgVBWFilter."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPCfgVBWFilter_cfunc is None:
                self.RFmxSpecAn_TXPCfgVBWFilter_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPCfgVBWFilter"
                )
                self.RFmxSpecAn_TXPCfgVBWFilter_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_TXPCfgVBWFilter_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPCfgVBWFilter_cfunc(
            vi, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
        )

    def RFmxSpecAn_IQCfgAcquisition(
        self, vi, selector_string, sample_rate, number_of_records, acquisition_time, pretrigger_time
    ):
        """RFmxSpecAn_IQCfgAcquisition."""
        with self._func_lock:
            if self.RFmxSpecAn_IQCfgAcquisition_cfunc is None:
                self.RFmxSpecAn_IQCfgAcquisition_cfunc = self._get_library_function(
                    "RFmxSpecAn_IQCfgAcquisition"
                )
                self.RFmxSpecAn_IQCfgAcquisition_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_IQCfgAcquisition_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IQCfgAcquisition_cfunc(
            vi, selector_string, sample_rate, number_of_records, acquisition_time, pretrigger_time
        )

    def RFmxSpecAn_IQCfgBandwidth(self, vi, selector_string, bandwidth_auto, bandwidth):
        """RFmxSpecAn_IQCfgBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_IQCfgBandwidth_cfunc is None:
                self.RFmxSpecAn_IQCfgBandwidth_cfunc = self._get_library_function(
                    "RFmxSpecAn_IQCfgBandwidth"
                )
                self.RFmxSpecAn_IQCfgBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_IQCfgBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IQCfgBandwidth_cfunc(vi, selector_string, bandwidth_auto, bandwidth)

    def RFmxSpecAn_PhaseNoiseCfgAutoRange(
        self, vi, selector_string, start_frequency, stop_frequency, rbw_percentage
    ):
        """RFmxSpecAn_PhaseNoiseCfgAutoRange."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgAutoRange_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgAutoRange_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgAutoRange"
                )
                self.RFmxSpecAn_PhaseNoiseCfgAutoRange_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgAutoRange_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgAutoRange_cfunc(
            vi, selector_string, start_frequency, stop_frequency, rbw_percentage
        )

    def RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier(
        self, vi, selector_string, averaging_multiplier
    ):
        """RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier"
                )
                self.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier_cfunc(
            vi, selector_string, averaging_multiplier
        )

    def RFmxSpecAn_PhaseNoiseCfgCancellation(
        self,
        vi,
        selector_string,
        cancellation_enabled,
        cancellation_threshold,
        frequency,
        reference_phase_noise,
        array_size,
    ):
        """RFmxSpecAn_PhaseNoiseCfgCancellation."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgCancellation_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgCancellation_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgCancellation"
                )
                self.RFmxSpecAn_PhaseNoiseCfgCancellation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgCancellation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgCancellation_cfunc(
            vi,
            selector_string,
            cancellation_enabled,
            cancellation_threshold,
            frequency,
            reference_phase_noise,
            array_size,
        )

    def RFmxSpecAn_PhaseNoiseCfgIntegratedNoise(
        self,
        vi,
        selector_string,
        integrated_noise_range_definition,
        integrated_noise_start_frequency,
        integrated_noise_stop_frequency,
        array_size,
    ):
        """RFmxSpecAn_PhaseNoiseCfgIntegratedNoise."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgIntegratedNoise"
                )
                self.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise_cfunc(
            vi,
            selector_string,
            integrated_noise_range_definition,
            integrated_noise_start_frequency,
            integrated_noise_stop_frequency,
            array_size,
        )

    def RFmxSpecAn_PhaseNoiseCfgNumberOfRanges(self, vi, selector_string, number_of_ranges):
        """RFmxSpecAn_PhaseNoiseCfgNumberOfRanges."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgNumberOfRanges"
                )
                self.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges_cfunc(
            vi, selector_string, number_of_ranges
        )

    def RFmxSpecAn_PhaseNoiseCfgRangeArray(
        self,
        vi,
        selector_string,
        range_start_frequency,
        range_stop_frequency,
        range_rbw_percentage,
        range_averaging_count,
        number_of_elements,
    ):
        """RFmxSpecAn_PhaseNoiseCfgRangeArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgRangeArray_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgRangeArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgRangeArray"
                )
                self.RFmxSpecAn_PhaseNoiseCfgRangeArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgRangeArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgRangeArray_cfunc(
            vi,
            selector_string,
            range_start_frequency,
            range_stop_frequency,
            range_rbw_percentage,
            range_averaging_count,
            number_of_elements,
        )

    def RFmxSpecAn_PhaseNoiseCfgRangeDefinition(self, vi, selector_string, range_definition):
        """RFmxSpecAn_PhaseNoiseCfgRangeDefinition."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgRangeDefinition_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgRangeDefinition_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgRangeDefinition"
                )
                self.RFmxSpecAn_PhaseNoiseCfgRangeDefinition_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgRangeDefinition_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgRangeDefinition_cfunc(
            vi, selector_string, range_definition
        )

    def RFmxSpecAn_PhaseNoiseCfgSmoothing(
        self, vi, selector_string, smoothing_type, smoothing_percentage
    ):
        """RFmxSpecAn_PhaseNoiseCfgSmoothing."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgSmoothing_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgSmoothing_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgSmoothing"
                )
                self.RFmxSpecAn_PhaseNoiseCfgSmoothing_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgSmoothing_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgSmoothing_cfunc(
            vi, selector_string, smoothing_type, smoothing_percentage
        )

    def RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList(
        self, vi, selector_string, frequency_list, array_size
    ):
        """RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList_cfunc = (
                    self._get_library_function("RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList")
                )
                self.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList_cfunc(
            vi, selector_string, frequency_list, array_size
        )

    def RFmxSpecAn_PhaseNoiseCfgSpurRemoval(
        self, vi, selector_string, spur_removal_enabled, peak_excursion
    ):
        """RFmxSpecAn_PhaseNoiseCfgSpurRemoval."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseCfgSpurRemoval_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseCfgSpurRemoval_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseCfgSpurRemoval"
                )
                self.RFmxSpecAn_PhaseNoiseCfgSpurRemoval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PhaseNoiseCfgSpurRemoval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseCfgSpurRemoval_cfunc(
            vi, selector_string, spur_removal_enabled, peak_excursion
        )

    def RFmxSpecAn_PAVTCfgMeasurementBandwidth(self, vi, selector_string, measurement_bandwidth):
        """RFmxSpecAn_PAVTCfgMeasurementBandwidth."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgMeasurementBandwidth_cfunc is None:
                self.RFmxSpecAn_PAVTCfgMeasurementBandwidth_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgMeasurementBandwidth"
                )
                self.RFmxSpecAn_PAVTCfgMeasurementBandwidth_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PAVTCfgMeasurementBandwidth_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgMeasurementBandwidth_cfunc(
            vi, selector_string, measurement_bandwidth
        )

    def RFmxSpecAn_PAVTCfgMeasurementIntervalMode(
        self, vi, selector_string, measurement_interval_mode
    ):
        """RFmxSpecAn_PAVTCfgMeasurementIntervalMode."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgMeasurementIntervalMode_cfunc is None:
                self.RFmxSpecAn_PAVTCfgMeasurementIntervalMode_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgMeasurementIntervalMode"
                )
                self.RFmxSpecAn_PAVTCfgMeasurementIntervalMode_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgMeasurementIntervalMode_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgMeasurementIntervalMode_cfunc(
            vi, selector_string, measurement_interval_mode
        )

    def RFmxSpecAn_PAVTCfgMeasurementInterval(
        self, vi, selector_string, measurement_offset, measurement_length
    ):
        """RFmxSpecAn_PAVTCfgMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_PAVTCfgMeasurementInterval_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgMeasurementInterval"
                )
                self.RFmxSpecAn_PAVTCfgMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PAVTCfgMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgMeasurementInterval_cfunc(
            vi, selector_string, measurement_offset, measurement_length
        )

    def RFmxSpecAn_PAVTCfgMeasurementLocationType(
        self, vi, selector_string, measurement_location_type
    ):
        """RFmxSpecAn_PAVTCfgMeasurementLocationType."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgMeasurementLocationType_cfunc is None:
                self.RFmxSpecAn_PAVTCfgMeasurementLocationType_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgMeasurementLocationType"
                )
                self.RFmxSpecAn_PAVTCfgMeasurementLocationType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgMeasurementLocationType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgMeasurementLocationType_cfunc(
            vi, selector_string, measurement_location_type
        )

    def RFmxSpecAn_PAVTCfgNumberOfSegments(self, vi, selector_string, number_of_segments):
        """RFmxSpecAn_PAVTCfgNumberOfSegments."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgNumberOfSegments_cfunc is None:
                self.RFmxSpecAn_PAVTCfgNumberOfSegments_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgNumberOfSegments"
                )
                self.RFmxSpecAn_PAVTCfgNumberOfSegments_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgNumberOfSegments_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgNumberOfSegments_cfunc(
            vi, selector_string, number_of_segments
        )

    def RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray(
        self,
        vi,
        selector_string,
        segment_measurement_offset,
        segment_measurement_length,
        number_of_elements,
    ):
        """RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray_cfunc is None:
                self.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray")
                )
                self.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray_cfunc(
            vi,
            selector_string,
            segment_measurement_offset,
            segment_measurement_length,
            number_of_elements,
        )

    def RFmxSpecAn_PAVTCfgSegmentMeasurementInterval(
        self, vi, selector_string, segment_measurement_offset, segment_measurement_length
    ):
        """RFmxSpecAn_PAVTCfgSegmentMeasurementInterval."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval_cfunc is None:
                self.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval_cfunc = (
                    self._get_library_function("RFmxSpecAn_PAVTCfgSegmentMeasurementInterval")
                )
                self.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval_cfunc(
            vi, selector_string, segment_measurement_offset, segment_measurement_length
        )

    def RFmxSpecAn_PAVTCfgSegmentStartTimeList(
        self, vi, selector_string, segment_start_time, number_of_elements
    ):
        """RFmxSpecAn_PAVTCfgSegmentStartTimeList."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgSegmentStartTimeList_cfunc is None:
                self.RFmxSpecAn_PAVTCfgSegmentStartTimeList_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgSegmentStartTimeList"
                )
                self.RFmxSpecAn_PAVTCfgSegmentStartTimeList_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgSegmentStartTimeList_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgSegmentStartTimeList_cfunc(
            vi, selector_string, segment_start_time, number_of_elements
        )

    def RFmxSpecAn_PAVTCfgSegmentTypeArray(
        self, vi, selector_string, segment_type, number_of_elements
    ):
        """RFmxSpecAn_PAVTCfgSegmentTypeArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgSegmentTypeArray_cfunc is None:
                self.RFmxSpecAn_PAVTCfgSegmentTypeArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgSegmentTypeArray"
                )
                self.RFmxSpecAn_PAVTCfgSegmentTypeArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgSegmentTypeArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgSegmentTypeArray_cfunc(
            vi, selector_string, segment_type, number_of_elements
        )

    def RFmxSpecAn_PAVTCfgSegmentType(self, vi, selector_string, segment_type):
        """RFmxSpecAn_PAVTCfgSegmentType."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTCfgSegmentType_cfunc is None:
                self.RFmxSpecAn_PAVTCfgSegmentType_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTCfgSegmentType"
                )
                self.RFmxSpecAn_PAVTCfgSegmentType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PAVTCfgSegmentType_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTCfgSegmentType_cfunc(vi, selector_string, segment_type)

    def RFmxSpecAn_PowerListCfgRBWFilterArray(
        self, vi, selector_string, rbw, rbw_filter_type, rrc_alpha, array_size
    ):
        """RFmxSpecAn_PowerListCfgRBWFilterArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PowerListCfgRBWFilterArray_cfunc is None:
                self.RFmxSpecAn_PowerListCfgRBWFilterArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_PowerListCfgRBWFilterArray"
                )
                self.RFmxSpecAn_PowerListCfgRBWFilterArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxSpecAn_PowerListCfgRBWFilterArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PowerListCfgRBWFilterArray_cfunc(
            vi, selector_string, rbw, rbw_filter_type, rrc_alpha, array_size
        )

    def RFmxSpecAn_CfgExternalAttenuation(self, vi, selector_string, external_attenuation):
        """RFmxSpecAn_CfgExternalAttenuation."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgExternalAttenuation_cfunc is None:
                self.RFmxSpecAn_CfgExternalAttenuation_cfunc = self._get_library_function(
                    "RFmxSpecAn_CfgExternalAttenuation"
                )
                self.RFmxSpecAn_CfgExternalAttenuation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CfgExternalAttenuation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgExternalAttenuation_cfunc(
            vi, selector_string, external_attenuation
        )

    def RFmxSpecAn_CfgFrequency(self, vi, selector_string, center_frequency):
        """RFmxSpecAn_CfgFrequency."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgFrequency_cfunc is None:
                self.RFmxSpecAn_CfgFrequency_cfunc = self._get_library_function(
                    "RFmxSpecAn_CfgFrequency"
                )
                self.RFmxSpecAn_CfgFrequency_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CfgFrequency_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgFrequency_cfunc(vi, selector_string, center_frequency)

    def RFmxSpecAn_CfgReferenceLevel(self, vi, selector_string, reference_level):
        """RFmxSpecAn_CfgReferenceLevel."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgReferenceLevel_cfunc is None:
                self.RFmxSpecAn_CfgReferenceLevel_cfunc = self._get_library_function(
                    "RFmxSpecAn_CfgReferenceLevel"
                )
                self.RFmxSpecAn_CfgReferenceLevel_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CfgReferenceLevel_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgReferenceLevel_cfunc(vi, selector_string, reference_level)

    def RFmxSpecAn_CfgRF(
        self, vi, selector_string, center_frequency, reference_level, external_attenuation
    ):
        """RFmxSpecAn_CfgRF."""
        with self._func_lock:
            if self.RFmxSpecAn_CfgRF_cfunc is None:
                self.RFmxSpecAn_CfgRF_cfunc = self._get_library_function("RFmxSpecAn_CfgRF")
                self.RFmxSpecAn_CfgRF_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxSpecAn_CfgRF_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CfgRF_cfunc(
            vi, selector_string, center_frequency, reference_level, external_attenuation
        )

    def RFmxSpecAn_IMFetchFundamentalMeasurement(
        self, vi, selector_string, timeout, lower_tone_power, upper_tone_power
    ):
        """RFmxSpecAn_IMFetchFundamentalMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_IMFetchFundamentalMeasurement_cfunc is None:
                self.RFmxSpecAn_IMFetchFundamentalMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMFetchFundamentalMeasurement"
                )
                self.RFmxSpecAn_IMFetchFundamentalMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_IMFetchFundamentalMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMFetchFundamentalMeasurement_cfunc(
            vi, selector_string, timeout, lower_tone_power, upper_tone_power
        )

    def RFmxSpecAn_IMFetchInterceptPower(
        self,
        vi,
        selector_string,
        timeout,
        intermod_order,
        worst_case_output_intercept_power,
        lower_output_intercept_power,
        upper_output_intercept_power,
    ):
        """RFmxSpecAn_IMFetchInterceptPower."""
        with self._func_lock:
            if self.RFmxSpecAn_IMFetchInterceptPower_cfunc is None:
                self.RFmxSpecAn_IMFetchInterceptPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMFetchInterceptPower"
                )
                self.RFmxSpecAn_IMFetchInterceptPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_IMFetchInterceptPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMFetchInterceptPower_cfunc(
            vi,
            selector_string,
            timeout,
            intermod_order,
            worst_case_output_intercept_power,
            lower_output_intercept_power,
            upper_output_intercept_power,
        )

    def RFmxSpecAn_IMFetchIntermodMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        intermod_order,
        lower_intermod_absolute_power,
        upper_intermod_absolute_power,
    ):
        """RFmxSpecAn_IMFetchIntermodMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_IMFetchIntermodMeasurement_cfunc is None:
                self.RFmxSpecAn_IMFetchIntermodMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMFetchIntermodMeasurement"
                )
                self.RFmxSpecAn_IMFetchIntermodMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_IMFetchIntermodMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMFetchIntermodMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            intermod_order,
            lower_intermod_absolute_power,
            upper_intermod_absolute_power,
        )

    def RFmxSpecAn_FCntFetchAllanDeviation(self, vi, selector_string, timeout, allan_deviation):
        """RFmxSpecAn_FCntFetchAllanDeviation."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntFetchAllanDeviation_cfunc is None:
                self.RFmxSpecAn_FCntFetchAllanDeviation_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntFetchAllanDeviation"
                )
                self.RFmxSpecAn_FCntFetchAllanDeviation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_FCntFetchAllanDeviation_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntFetchAllanDeviation_cfunc(
            vi, selector_string, timeout, allan_deviation
        )

    def RFmxSpecAn_FCntFetchMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        average_relative_frequency,
        average_absolute_frequency,
        mean_phase,
    ):
        """RFmxSpecAn_FCntFetchMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntFetchMeasurement_cfunc is None:
                self.RFmxSpecAn_FCntFetchMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntFetchMeasurement"
                )
                self.RFmxSpecAn_FCntFetchMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_FCntFetchMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntFetchMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            average_relative_frequency,
            average_absolute_frequency,
            mean_phase,
        )

    def RFmxSpecAn_FCntRead(
        self,
        vi,
        selector_string,
        timeout,
        average_relative_frequency,
        average_absolute_frequency,
        mean_phase,
    ):
        """RFmxSpecAn_FCntRead."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntRead_cfunc is None:
                self.RFmxSpecAn_FCntRead_cfunc = self._get_library_function("RFmxSpecAn_FCntRead")
                self.RFmxSpecAn_FCntRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_FCntRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntRead_cfunc(
            vi,
            selector_string,
            timeout,
            average_relative_frequency,
            average_absolute_frequency,
            mean_phase,
        )

    def RFmxSpecAn_SpectrumFetchMeasurement(
        self, vi, selector_string, timeout, peak_amplitude, peak_frequency, frequency_resolution
    ):
        """RFmxSpecAn_SpectrumFetchMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumFetchMeasurement_cfunc is None:
                self.RFmxSpecAn_SpectrumFetchMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumFetchMeasurement"
                )
                self.RFmxSpecAn_SpectrumFetchMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SpectrumFetchMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumFetchMeasurement_cfunc(
            vi, selector_string, timeout, peak_amplitude, peak_frequency, frequency_resolution
        )

    def RFmxSpecAn_SpurFetchMeasurementStatus(
        self, vi, selector_string, timeout, measurement_status
    ):
        """RFmxSpecAn_SpurFetchMeasurementStatus."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchMeasurementStatus_cfunc is None:
                self.RFmxSpecAn_SpurFetchMeasurementStatus_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchMeasurementStatus"
                )
                self.RFmxSpecAn_SpurFetchMeasurementStatus_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchMeasurementStatus_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchMeasurementStatus_cfunc(
            vi, selector_string, timeout, measurement_status
        )

    def RFmxSpecAn_SpurFetchRangeStatus(
        self, vi, selector_string, timeout, range_status, detected_spurs
    ):
        """RFmxSpecAn_SpurFetchRangeStatus."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchRangeStatus_cfunc is None:
                self.RFmxSpecAn_SpurFetchRangeStatus_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchRangeStatus"
                )
                self.RFmxSpecAn_SpurFetchRangeStatus_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchRangeStatus_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchRangeStatus_cfunc(
            vi, selector_string, timeout, range_status, detected_spurs
        )

    def RFmxSpecAn_SpurFetchSpurMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        spur_frequency,
        spur_amplitude,
        spur_margin,
        spur_absolute_limit,
    ):
        """RFmxSpecAn_SpurFetchSpurMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchSpurMeasurement_cfunc is None:
                self.RFmxSpecAn_SpurFetchSpurMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchSpurMeasurement"
                )
                self.RFmxSpecAn_SpurFetchSpurMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SpurFetchSpurMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchSpurMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            spur_frequency,
            spur_amplitude,
            spur_margin,
            spur_absolute_limit,
        )

    def RFmxSpecAn_AMPMFetchCurveFitResidual(
        self, vi, selector_string, timeout, am_to_am_residual, am_to_pm_residual
    ):
        """RFmxSpecAn_AMPMFetchCurveFitResidual."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchCurveFitResidual_cfunc is None:
                self.RFmxSpecAn_AMPMFetchCurveFitResidual_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchCurveFitResidual"
                )
                self.RFmxSpecAn_AMPMFetchCurveFitResidual_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_AMPMFetchCurveFitResidual_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchCurveFitResidual_cfunc(
            vi, selector_string, timeout, am_to_am_residual, am_to_pm_residual
        )

    def RFmxSpecAn_AMPMFetchDUTCharacteristics(
        self, vi, selector_string, timeout, mean_linear_gain, one_db_compression_point, mean_rms_evm
    ):
        """RFmxSpecAn_AMPMFetchDUTCharacteristics."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchDUTCharacteristics_cfunc is None:
                self.RFmxSpecAn_AMPMFetchDUTCharacteristics_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchDUTCharacteristics"
                )
                self.RFmxSpecAn_AMPMFetchDUTCharacteristics_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_AMPMFetchDUTCharacteristics_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchDUTCharacteristics_cfunc(
            vi, selector_string, timeout, mean_linear_gain, one_db_compression_point, mean_rms_evm
        )

    def RFmxSpecAn_AMPMFetchError(
        self, vi, selector_string, timeout, gain_error_range, phase_error_range, mean_phase_error
    ):
        """RFmxSpecAn_AMPMFetchError."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchError_cfunc is None:
                self.RFmxSpecAn_AMPMFetchError_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchError"
                )
                self.RFmxSpecAn_AMPMFetchError_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_AMPMFetchError_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchError_cfunc(
            vi, selector_string, timeout, gain_error_range, phase_error_range, mean_phase_error
        )

    def RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR(self, vi, selector_string, timeout, pre_cfr_papr):
        """RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR_cfunc is None:
                self.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR"
                )
                self.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR_cfunc(
            vi, selector_string, timeout, pre_cfr_papr
        )

    def RFmxSpecAn_DPDFetchAverageGain(self, vi, selector_string, timeout, average_gain):
        """RFmxSpecAn_DPDFetchAverageGain."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchAverageGain_cfunc is None:
                self.RFmxSpecAn_DPDFetchAverageGain_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDFetchAverageGain"
                )
                self.RFmxSpecAn_DPDFetchAverageGain_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_DPDFetchAverageGain_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchAverageGain_cfunc(vi, selector_string, timeout, average_gain)

    def RFmxSpecAn_DPDFetchNMSE(self, vi, selector_string, timeout, nmse):
        """RFmxSpecAn_DPDFetchNMSE."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchNMSE_cfunc is None:
                self.RFmxSpecAn_DPDFetchNMSE_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDFetchNMSE"
                )
                self.RFmxSpecAn_DPDFetchNMSE_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_DPDFetchNMSE_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchNMSE_cfunc(vi, selector_string, timeout, nmse)

    def RFmxSpecAn_ACPFetchCarrierMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        absolute_power,
        total_relative_power,
        carrier_offset,
        integration_bandwidth,
    ):
        """RFmxSpecAn_ACPFetchCarrierMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchCarrierMeasurement_cfunc is None:
                self.RFmxSpecAn_ACPFetchCarrierMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchCarrierMeasurement"
                )
                self.RFmxSpecAn_ACPFetchCarrierMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_ACPFetchCarrierMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchCarrierMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            absolute_power,
            total_relative_power,
            carrier_offset,
            integration_bandwidth,
        )

    def RFmxSpecAn_ACPFetchFrequencyResolution(
        self, vi, selector_string, timeout, frequency_resolution
    ):
        """RFmxSpecAn_ACPFetchFrequencyResolution."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchFrequencyResolution_cfunc is None:
                self.RFmxSpecAn_ACPFetchFrequencyResolution_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchFrequencyResolution"
                )
                self.RFmxSpecAn_ACPFetchFrequencyResolution_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_ACPFetchFrequencyResolution_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchFrequencyResolution_cfunc(
            vi, selector_string, timeout, frequency_resolution
        )

    def RFmxSpecAn_ACPFetchOffsetMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        lower_relative_power,
        upper_relative_power,
        lower_absolute_power,
        upper_absolute_power,
    ):
        """RFmxSpecAn_ACPFetchOffsetMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchOffsetMeasurement_cfunc is None:
                self.RFmxSpecAn_ACPFetchOffsetMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchOffsetMeasurement"
                )
                self.RFmxSpecAn_ACPFetchOffsetMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_ACPFetchOffsetMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchOffsetMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            lower_relative_power,
            upper_relative_power,
            lower_absolute_power,
            upper_absolute_power,
        )

    def RFmxSpecAn_ACPFetchTotalCarrierPower(
        self, vi, selector_string, timeout, total_carrier_power
    ):
        """RFmxSpecAn_ACPFetchTotalCarrierPower."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchTotalCarrierPower_cfunc is None:
                self.RFmxSpecAn_ACPFetchTotalCarrierPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchTotalCarrierPower"
                )
                self.RFmxSpecAn_ACPFetchTotalCarrierPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_ACPFetchTotalCarrierPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchTotalCarrierPower_cfunc(
            vi, selector_string, timeout, total_carrier_power
        )

    def RFmxSpecAn_ACPRead(
        self,
        vi,
        selector_string,
        timeout,
        carrier_absolute_power,
        offset_ch0_lower_relative_power,
        offset_ch0_upper_relative_power,
        offset_ch1_lower_relative_power,
        offset_ch1_upper_relative_power,
    ):
        """RFmxSpecAn_ACPRead."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPRead_cfunc is None:
                self.RFmxSpecAn_ACPRead_cfunc = self._get_library_function("RFmxSpecAn_ACPRead")
                self.RFmxSpecAn_ACPRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_ACPRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPRead_cfunc(
            vi,
            selector_string,
            timeout,
            carrier_absolute_power,
            offset_ch0_lower_relative_power,
            offset_ch0_upper_relative_power,
            offset_ch1_lower_relative_power,
            offset_ch1_upper_relative_power,
        )

    def RFmxSpecAn_CCDFFetchBasicPowerProbabilities(
        self,
        vi,
        selector_string,
        timeout,
        ten_percent_power,
        one_percent_power,
        one_tenth_percent_power,
        one_hundredth_percent_power,
        one_thousandth_percent_power,
        one_ten_thousandth_percent_power,
    ):
        """RFmxSpecAn_CCDFFetchBasicPowerProbabilities."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFFetchBasicPowerProbabilities_cfunc is None:
                self.RFmxSpecAn_CCDFFetchBasicPowerProbabilities_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFFetchBasicPowerProbabilities"
                )
                self.RFmxSpecAn_CCDFFetchBasicPowerProbabilities_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_CCDFFetchBasicPowerProbabilities_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFFetchBasicPowerProbabilities_cfunc(
            vi,
            selector_string,
            timeout,
            ten_percent_power,
            one_percent_power,
            one_tenth_percent_power,
            one_hundredth_percent_power,
            one_thousandth_percent_power,
            one_ten_thousandth_percent_power,
        )

    def RFmxSpecAn_CCDFFetchPower(
        self,
        vi,
        selector_string,
        timeout,
        mean_power,
        mean_power_percentile,
        peak_power,
        measured_samples_count,
    ):
        """RFmxSpecAn_CCDFFetchPower."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFFetchPower_cfunc is None:
                self.RFmxSpecAn_CCDFFetchPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFFetchPower"
                )
                self.RFmxSpecAn_CCDFFetchPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CCDFFetchPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFFetchPower_cfunc(
            vi,
            selector_string,
            timeout,
            mean_power,
            mean_power_percentile,
            peak_power,
            measured_samples_count,
        )

    def RFmxSpecAn_CCDFRead(
        self,
        vi,
        selector_string,
        timeout,
        mean_power,
        mean_power_percentile,
        peak_power,
        measured_samples_count,
    ):
        """RFmxSpecAn_CCDFRead."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFRead_cfunc is None:
                self.RFmxSpecAn_CCDFRead_cfunc = self._get_library_function("RFmxSpecAn_CCDFRead")
                self.RFmxSpecAn_CCDFRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CCDFRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFRead_cfunc(
            vi,
            selector_string,
            timeout,
            mean_power,
            mean_power_percentile,
            peak_power,
            measured_samples_count,
        )

    def RFmxSpecAn_CHPFetchTotalCarrierPower(
        self, vi, selector_string, timeout, total_carrier_power
    ):
        """RFmxSpecAn_CHPFetchTotalCarrierPower."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPFetchTotalCarrierPower_cfunc is None:
                self.RFmxSpecAn_CHPFetchTotalCarrierPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPFetchTotalCarrierPower"
                )
                self.RFmxSpecAn_CHPFetchTotalCarrierPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_CHPFetchTotalCarrierPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPFetchTotalCarrierPower_cfunc(
            vi, selector_string, timeout, total_carrier_power
        )

    def RFmxSpecAn_CHPRead(self, vi, selector_string, timeout, absolute_power, psd):
        """RFmxSpecAn_CHPRead."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPRead_cfunc is None:
                self.RFmxSpecAn_CHPRead_cfunc = self._get_library_function("RFmxSpecAn_CHPRead")
                self.RFmxSpecAn_CHPRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_CHPRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPRead_cfunc(vi, selector_string, timeout, absolute_power, psd)

    def RFmxSpecAn_HarmFetchHarmonicMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        average_relative_power,
        average_absolute_power,
        rbw,
        frequency,
    ):
        """RFmxSpecAn_HarmFetchHarmonicMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmFetchHarmonicMeasurement_cfunc is None:
                self.RFmxSpecAn_HarmFetchHarmonicMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmFetchHarmonicMeasurement"
                )
                self.RFmxSpecAn_HarmFetchHarmonicMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_HarmFetchHarmonicMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmFetchHarmonicMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            average_relative_power,
            average_absolute_power,
            rbw,
            frequency,
        )

    def RFmxSpecAn_HarmFetchTHD(
        self,
        vi,
        selector_string,
        timeout,
        total_harmonic_distortion,
        average_fundamental_power,
        fundamental_frequency,
    ):
        """RFmxSpecAn_HarmFetchTHD."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmFetchTHD_cfunc is None:
                self.RFmxSpecAn_HarmFetchTHD_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmFetchTHD"
                )
                self.RFmxSpecAn_HarmFetchTHD_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_HarmFetchTHD_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmFetchTHD_cfunc(
            vi,
            selector_string,
            timeout,
            total_harmonic_distortion,
            average_fundamental_power,
            fundamental_frequency,
        )

    def RFmxSpecAn_HarmRead(
        self, vi, selector_string, timeout, total_harmonic_distortion, average_fundamental_power
    ):
        """RFmxSpecAn_HarmRead."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmRead_cfunc is None:
                self.RFmxSpecAn_HarmRead_cfunc = self._get_library_function("RFmxSpecAn_HarmRead")
                self.RFmxSpecAn_HarmRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_HarmRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmRead_cfunc(
            vi, selector_string, timeout, total_harmonic_distortion, average_fundamental_power
        )

    def RFmxSpecAn_MarkerFetchXY(self, vi, selector_string, marker_x_location, marker_y_location):
        """RFmxSpecAn_MarkerFetchXY."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerFetchXY_cfunc is None:
                self.RFmxSpecAn_MarkerFetchXY_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerFetchXY"
                )
                self.RFmxSpecAn_MarkerFetchXY_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_MarkerFetchXY_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerFetchXY_cfunc(
            vi, selector_string, marker_x_location, marker_y_location
        )

    def RFmxSpecAn_MarkerNextPeak(self, vi, selector_string, next_peak, next_peak_found):
        """RFmxSpecAn_MarkerNextPeak."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerNextPeak_cfunc is None:
                self.RFmxSpecAn_MarkerNextPeak_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerNextPeak"
                )
                self.RFmxSpecAn_MarkerNextPeak_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_MarkerNextPeak_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerNextPeak_cfunc(vi, selector_string, next_peak, next_peak_found)

    def RFmxSpecAn_MarkerPeakSearch(self, vi, selector_string, number_of_peaks):
        """RFmxSpecAn_MarkerPeakSearch."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerPeakSearch_cfunc is None:
                self.RFmxSpecAn_MarkerPeakSearch_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerPeakSearch"
                )
                self.RFmxSpecAn_MarkerPeakSearch_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_MarkerPeakSearch_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerPeakSearch_cfunc(vi, selector_string, number_of_peaks)

    def RFmxSpecAn_MarkerFetchFunctionValue(self, vi, selector_string, function_value):
        """RFmxSpecAn_MarkerFetchFunctionValue."""
        with self._func_lock:
            if self.RFmxSpecAn_MarkerFetchFunctionValue_cfunc is None:
                self.RFmxSpecAn_MarkerFetchFunctionValue_cfunc = self._get_library_function(
                    "RFmxSpecAn_MarkerFetchFunctionValue"
                )
                self.RFmxSpecAn_MarkerFetchFunctionValue_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_MarkerFetchFunctionValue_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_MarkerFetchFunctionValue_cfunc(vi, selector_string, function_value)

    def RFmxSpecAn_SEMFetchCarrierMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        absolute_power,
        peak_absolute_power,
        peak_frequency,
        total_relative_power,
    ):
        """RFmxSpecAn_SEMFetchCarrierMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchCarrierMeasurement_cfunc is None:
                self.RFmxSpecAn_SEMFetchCarrierMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchCarrierMeasurement"
                )
                self.RFmxSpecAn_SEMFetchCarrierMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchCarrierMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchCarrierMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            absolute_power,
            peak_absolute_power,
            peak_frequency,
            total_relative_power,
        )

    def RFmxSpecAn_SEMFetchCompositeMeasurementStatus(
        self, vi, selector_string, timeout, composite_measurement_status
    ):
        """RFmxSpecAn_SEMFetchCompositeMeasurementStatus."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchCompositeMeasurementStatus_cfunc is None:
                self.RFmxSpecAn_SEMFetchCompositeMeasurementStatus_cfunc = (
                    self._get_library_function("RFmxSpecAn_SEMFetchCompositeMeasurementStatus")
                )
                self.RFmxSpecAn_SEMFetchCompositeMeasurementStatus_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchCompositeMeasurementStatus_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchCompositeMeasurementStatus_cfunc(
            vi, selector_string, timeout, composite_measurement_status
        )

    def RFmxSpecAn_SEMFetchFrequencyResolution(
        self, vi, selector_string, timeout, frequency_resolution
    ):
        """RFmxSpecAn_SEMFetchFrequencyResolution."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchFrequencyResolution_cfunc is None:
                self.RFmxSpecAn_SEMFetchFrequencyResolution_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchFrequencyResolution"
                )
                self.RFmxSpecAn_SEMFetchFrequencyResolution_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchFrequencyResolution_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchFrequencyResolution_cfunc(
            vi, selector_string, timeout, frequency_resolution
        )

    def RFmxSpecAn_SEMFetchLowerOffsetMargin(
        self,
        vi,
        selector_string,
        timeout,
        measurement_status,
        margin,
        margin_frequency,
        margin_absolute_power,
        margin_relative_power,
    ):
        """RFmxSpecAn_SEMFetchLowerOffsetMargin."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchLowerOffsetMargin_cfunc is None:
                self.RFmxSpecAn_SEMFetchLowerOffsetMargin_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchLowerOffsetMargin"
                )
                self.RFmxSpecAn_SEMFetchLowerOffsetMargin_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchLowerOffsetMargin_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchLowerOffsetMargin_cfunc(
            vi,
            selector_string,
            timeout,
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
        )

    def RFmxSpecAn_SEMFetchLowerOffsetPower(
        self,
        vi,
        selector_string,
        timeout,
        total_absolute_power,
        total_relative_power,
        peak_absolute_power,
        peak_frequency,
        peak_relative_power,
    ):
        """RFmxSpecAn_SEMFetchLowerOffsetPower."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchLowerOffsetPower_cfunc is None:
                self.RFmxSpecAn_SEMFetchLowerOffsetPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchLowerOffsetPower"
                )
                self.RFmxSpecAn_SEMFetchLowerOffsetPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchLowerOffsetPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchLowerOffsetPower_cfunc(
            vi,
            selector_string,
            timeout,
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
        )

    def RFmxSpecAn_SEMFetchTotalCarrierPower(
        self, vi, selector_string, timeout, total_carrier_power
    ):
        """RFmxSpecAn_SEMFetchTotalCarrierPower."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchTotalCarrierPower_cfunc is None:
                self.RFmxSpecAn_SEMFetchTotalCarrierPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchTotalCarrierPower"
                )
                self.RFmxSpecAn_SEMFetchTotalCarrierPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchTotalCarrierPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchTotalCarrierPower_cfunc(
            vi, selector_string, timeout, total_carrier_power
        )

    def RFmxSpecAn_SEMFetchUpperOffsetMargin(
        self,
        vi,
        selector_string,
        timeout,
        measurement_status,
        margin,
        margin_frequency,
        margin_absolute_power,
        margin_relative_power,
    ):
        """RFmxSpecAn_SEMFetchUpperOffsetMargin."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchUpperOffsetMargin_cfunc is None:
                self.RFmxSpecAn_SEMFetchUpperOffsetMargin_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchUpperOffsetMargin"
                )
                self.RFmxSpecAn_SEMFetchUpperOffsetMargin_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchUpperOffsetMargin_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchUpperOffsetMargin_cfunc(
            vi,
            selector_string,
            timeout,
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
        )

    def RFmxSpecAn_SEMFetchUpperOffsetPower(
        self,
        vi,
        selector_string,
        timeout,
        total_absolute_power,
        total_relative_power,
        peak_absolute_power,
        peak_frequency,
        peak_relative_power,
    ):
        """RFmxSpecAn_SEMFetchUpperOffsetPower."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchUpperOffsetPower_cfunc is None:
                self.RFmxSpecAn_SEMFetchUpperOffsetPower_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchUpperOffsetPower"
                )
                self.RFmxSpecAn_SEMFetchUpperOffsetPower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_SEMFetchUpperOffsetPower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchUpperOffsetPower_cfunc(
            vi,
            selector_string,
            timeout,
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
        )

    def RFmxSpecAn_OBWFetchMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        occupied_bandwidth,
        average_power,
        frequency_resolution,
        start_frequency,
        stop_frequency,
    ):
        """RFmxSpecAn_OBWFetchMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWFetchMeasurement_cfunc is None:
                self.RFmxSpecAn_OBWFetchMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWFetchMeasurement"
                )
                self.RFmxSpecAn_OBWFetchMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_OBWFetchMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWFetchMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            occupied_bandwidth,
            average_power,
            frequency_resolution,
            start_frequency,
            stop_frequency,
        )

    def RFmxSpecAn_OBWRead(
        self,
        vi,
        selector_string,
        timeout,
        occupied_bandwidth,
        average_power,
        frequency_resolution,
        start_frequency,
        stop_frequency,
    ):
        """RFmxSpecAn_OBWRead."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWRead_cfunc is None:
                self.RFmxSpecAn_OBWRead_cfunc = self._get_library_function("RFmxSpecAn_OBWRead")
                self.RFmxSpecAn_OBWRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_OBWRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWRead_cfunc(
            vi,
            selector_string,
            timeout,
            occupied_bandwidth,
            average_power,
            frequency_resolution,
            start_frequency,
            stop_frequency,
        )

    def RFmxSpecAn_TXPFetchMeasurement(
        self,
        vi,
        selector_string,
        timeout,
        average_mean_power,
        peak_to_average_ratio,
        maximum_power,
        minimum_power,
    ):
        """RFmxSpecAn_TXPFetchMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPFetchMeasurement_cfunc is None:
                self.RFmxSpecAn_TXPFetchMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPFetchMeasurement"
                )
                self.RFmxSpecAn_TXPFetchMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_TXPFetchMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPFetchMeasurement_cfunc(
            vi,
            selector_string,
            timeout,
            average_mean_power,
            peak_to_average_ratio,
            maximum_power,
            minimum_power,
        )

    def RFmxSpecAn_TXPRead(
        self,
        vi,
        selector_string,
        timeout,
        average_mean_power,
        peak_to_average_ratio,
        maximum_power,
        minimum_power,
    ):
        """RFmxSpecAn_TXPRead."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPRead_cfunc is None:
                self.RFmxSpecAn_TXPRead_cfunc = self._get_library_function("RFmxSpecAn_TXPRead")
                self.RFmxSpecAn_TXPRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_TXPRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPRead_cfunc(
            vi,
            selector_string,
            timeout,
            average_mean_power,
            peak_to_average_ratio,
            maximum_power,
            minimum_power,
        )

    def RFmxSpecAn_IQGetRecordsDone(self, vi, selector_string, records_done):
        """RFmxSpecAn_IQGetRecordsDone."""
        with self._func_lock:
            if self.RFmxSpecAn_IQGetRecordsDone_cfunc is None:
                self.RFmxSpecAn_IQGetRecordsDone_cfunc = self._get_library_function(
                    "RFmxSpecAn_IQGetRecordsDone"
                )
                self.RFmxSpecAn_IQGetRecordsDone_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IQGetRecordsDone_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IQGetRecordsDone_cfunc(vi, selector_string, records_done)

    def RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement(
        self, vi, selector_string, timeout, carrier_frequency, carrier_power
    ):
        """RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement_cfunc = (
                    self._get_library_function("RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement")
                )
                self.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement_cfunc(
            vi, selector_string, timeout, carrier_frequency, carrier_power
        )

    def RFmxSpecAn_PAVTFetchPhaseAndAmplitude(
        self,
        vi,
        selector_string,
        timeout,
        mean_relative_phase,
        mean_relative_amplitude,
        mean_absolute_phase,
        mean_absolute_amplitude,
    ):
        """RFmxSpecAn_PAVTFetchPhaseAndAmplitude."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTFetchPhaseAndAmplitude_cfunc is None:
                self.RFmxSpecAn_PAVTFetchPhaseAndAmplitude_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTFetchPhaseAndAmplitude"
                )
                self.RFmxSpecAn_PAVTFetchPhaseAndAmplitude_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_PAVTFetchPhaseAndAmplitude_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTFetchPhaseAndAmplitude_cfunc(
            vi,
            selector_string,
            timeout,
            mean_relative_phase,
            mean_relative_amplitude,
            mean_absolute_phase,
            mean_absolute_amplitude,
        )

    def RFmxSpecAn_CHPFetchCarrierMeasurement(
        self, vi, selector_string, timeout, absolute_power, psd, relative_power
    ):
        """RFmxSpecAn_CHPFetchCarrierMeasurement."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPFetchCarrierMeasurement_cfunc is None:
                self.RFmxSpecAn_CHPFetchCarrierMeasurement_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPFetchCarrierMeasurement"
                )
                self.RFmxSpecAn_CHPFetchCarrierMeasurement_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_CHPFetchCarrierMeasurement_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPFetchCarrierMeasurement_cfunc(
            vi, selector_string, timeout, absolute_power, psd, relative_power
        )

    def RFmxSpecAn_IMFetchInterceptPowerArray(
        self,
        vi,
        selector_string,
        timeout,
        intermod_order,
        worst_case_output_intercept_power,
        lower_output_intercept_power,
        upper_output_intercept_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IMFetchInterceptPowerArray."""
        with self._func_lock:
            if self.RFmxSpecAn_IMFetchInterceptPowerArray_cfunc is None:
                self.RFmxSpecAn_IMFetchInterceptPowerArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMFetchInterceptPowerArray"
                )
                self.RFmxSpecAn_IMFetchInterceptPowerArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IMFetchInterceptPowerArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMFetchInterceptPowerArray_cfunc(
            vi,
            selector_string,
            timeout,
            intermod_order,
            worst_case_output_intercept_power,
            lower_output_intercept_power,
            upper_output_intercept_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_IMFetchIntermodMeasurementArray(
        self,
        vi,
        selector_string,
        timeout,
        intermod_order,
        lower_intermod_absolute_power,
        upper_intermod_absolute_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IMFetchIntermodMeasurementArray."""
        with self._func_lock:
            if self.RFmxSpecAn_IMFetchIntermodMeasurementArray_cfunc is None:
                self.RFmxSpecAn_IMFetchIntermodMeasurementArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMFetchIntermodMeasurementArray"
                )
                self.RFmxSpecAn_IMFetchIntermodMeasurementArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IMFetchIntermodMeasurementArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMFetchIntermodMeasurementArray_cfunc(
            vi,
            selector_string,
            timeout,
            intermod_order,
            lower_intermod_absolute_power,
            upper_intermod_absolute_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_IMFetchSpectrum(
        self,
        vi,
        selector_string,
        timeout,
        spectrum_index,
        x0,
        dx,
        spectrum,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IMFetchSpectrum."""
        with self._func_lock:
            if self.RFmxSpecAn_IMFetchSpectrum_cfunc is None:
                self.RFmxSpecAn_IMFetchSpectrum_cfunc = self._get_library_function(
                    "RFmxSpecAn_IMFetchSpectrum"
                )
                self.RFmxSpecAn_IMFetchSpectrum_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IMFetchSpectrum_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IMFetchSpectrum_cfunc(
            vi,
            selector_string,
            timeout,
            spectrum_index,
            x0,
            dx,
            spectrum,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_NFFetchAnalyzerNoiseFigure(
        self, vi, selector_string, timeout, analyzer_noise_figure, array_size, actual_array_size
    ):
        """RFmxSpecAn_NFFetchAnalyzerNoiseFigure."""
        with self._func_lock:
            if self.RFmxSpecAn_NFFetchAnalyzerNoiseFigure_cfunc is None:
                self.RFmxSpecAn_NFFetchAnalyzerNoiseFigure_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFFetchAnalyzerNoiseFigure"
                )
                self.RFmxSpecAn_NFFetchAnalyzerNoiseFigure_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_NFFetchAnalyzerNoiseFigure_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFFetchAnalyzerNoiseFigure_cfunc(
            vi, selector_string, timeout, analyzer_noise_figure, array_size, actual_array_size
        )

    def RFmxSpecAn_NFFetchColdSourcePower(
        self, vi, selector_string, timeout, cold_source_power, array_size, actual_array_size
    ):
        """RFmxSpecAn_NFFetchColdSourcePower."""
        with self._func_lock:
            if self.RFmxSpecAn_NFFetchColdSourcePower_cfunc is None:
                self.RFmxSpecAn_NFFetchColdSourcePower_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFFetchColdSourcePower"
                )
                self.RFmxSpecAn_NFFetchColdSourcePower_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_NFFetchColdSourcePower_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFFetchColdSourcePower_cfunc(
            vi, selector_string, timeout, cold_source_power, array_size, actual_array_size
        )

    def RFmxSpecAn_NFFetchDUTNoiseFigureAndGain(
        self,
        vi,
        selector_string,
        timeout,
        dut_noise_figure,
        dut_noise_temperature,
        dut_gain,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_NFFetchDUTNoiseFigureAndGain."""
        with self._func_lock:
            if self.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain_cfunc is None:
                self.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFFetchDUTNoiseFigureAndGain"
                )
                self.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain_cfunc(
            vi,
            selector_string,
            timeout,
            dut_noise_figure,
            dut_noise_temperature,
            dut_gain,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_NFFetchYFactorPowers(
        self, vi, selector_string, timeout, hot_power, cold_power, array_size, actual_array_size
    ):
        """RFmxSpecAn_NFFetchYFactorPowers."""
        with self._func_lock:
            if self.RFmxSpecAn_NFFetchYFactorPowers_cfunc is None:
                self.RFmxSpecAn_NFFetchYFactorPowers_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFFetchYFactorPowers"
                )
                self.RFmxSpecAn_NFFetchYFactorPowers_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_NFFetchYFactorPowers_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFFetchYFactorPowers_cfunc(
            vi, selector_string, timeout, hot_power, cold_power, array_size, actual_array_size
        )

    def RFmxSpecAn_NFFetchYFactors(
        self,
        vi,
        selector_string,
        timeout,
        measurement_y_factor,
        calibration_y_factor,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_NFFetchYFactors."""
        with self._func_lock:
            if self.RFmxSpecAn_NFFetchYFactors_cfunc is None:
                self.RFmxSpecAn_NFFetchYFactors_cfunc = self._get_library_function(
                    "RFmxSpecAn_NFFetchYFactors"
                )
                self.RFmxSpecAn_NFFetchYFactors_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_NFFetchYFactors_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_NFFetchYFactors_cfunc(
            vi,
            selector_string,
            timeout,
            measurement_y_factor,
            calibration_y_factor,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_FCntFetchFrequencyTrace(
        self, vi, selector_string, timeout, x0, dx, frequency_trace, array_size, actual_array_size
    ):
        """RFmxSpecAn_FCntFetchFrequencyTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntFetchFrequencyTrace_cfunc is None:
                self.RFmxSpecAn_FCntFetchFrequencyTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntFetchFrequencyTrace"
                )
                self.RFmxSpecAn_FCntFetchFrequencyTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_FCntFetchFrequencyTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntFetchFrequencyTrace_cfunc(
            vi, selector_string, timeout, x0, dx, frequency_trace, array_size, actual_array_size
        )

    def RFmxSpecAn_FCntFetchPhaseTrace(
        self, vi, selector_string, timeout, x0, dx, phase_trace, array_size, actual_array_size
    ):
        """RFmxSpecAn_FCntFetchPhaseTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntFetchPhaseTrace_cfunc is None:
                self.RFmxSpecAn_FCntFetchPhaseTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntFetchPhaseTrace"
                )
                self.RFmxSpecAn_FCntFetchPhaseTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_FCntFetchPhaseTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntFetchPhaseTrace_cfunc(
            vi, selector_string, timeout, x0, dx, phase_trace, array_size, actual_array_size
        )

    def RFmxSpecAn_FCntFetchPowerTrace(
        self, vi, selector_string, timeout, x0, dx, power_trace, array_size, actual_array_size
    ):
        """RFmxSpecAn_FCntFetchPowerTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_FCntFetchPowerTrace_cfunc is None:
                self.RFmxSpecAn_FCntFetchPowerTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_FCntFetchPowerTrace"
                )
                self.RFmxSpecAn_FCntFetchPowerTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_FCntFetchPowerTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_FCntFetchPowerTrace_cfunc(
            vi, selector_string, timeout, x0, dx, power_trace, array_size, actual_array_size
        )

    def RFmxSpecAn_SpectrumFetchPowerTrace(
        self, vi, selector_string, timeout, x0, dx, power, array_size, actual_array_size
    ):
        """RFmxSpecAn_SpectrumFetchPowerTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumFetchPowerTrace_cfunc is None:
                self.RFmxSpecAn_SpectrumFetchPowerTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumFetchPowerTrace"
                )
                self.RFmxSpecAn_SpectrumFetchPowerTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpectrumFetchPowerTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumFetchPowerTrace_cfunc(
            vi, selector_string, timeout, x0, dx, power, array_size, actual_array_size
        )

    def RFmxSpecAn_SpectrumFetchSpectrum(
        self, vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_SpectrumFetchSpectrum."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumFetchSpectrum_cfunc is None:
                self.RFmxSpecAn_SpectrumFetchSpectrum_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumFetchSpectrum"
                )
                self.RFmxSpecAn_SpectrumFetchSpectrum_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpectrumFetchSpectrum_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumFetchSpectrum_cfunc(
            vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_SpectrumRead(
        self, vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_SpectrumRead."""
        with self._func_lock:
            if self.RFmxSpecAn_SpectrumRead_cfunc is None:
                self.RFmxSpecAn_SpectrumRead_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpectrumRead"
                )
                self.RFmxSpecAn_SpectrumRead_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpectrumRead_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpectrumRead_cfunc(
            vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_SpurFetchAllSpurs(
        self,
        vi,
        selector_string,
        timeout,
        spur_frequency,
        spur_amplitude,
        spur_margin,
        spur_absolute_limit,
        spur_range_index,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SpurFetchAllSpurs."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchAllSpurs_cfunc is None:
                self.RFmxSpecAn_SpurFetchAllSpurs_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchAllSpurs"
                )
                self.RFmxSpecAn_SpurFetchAllSpurs_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchAllSpurs_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchAllSpurs_cfunc(
            vi,
            selector_string,
            timeout,
            spur_frequency,
            spur_amplitude,
            spur_margin,
            spur_absolute_limit,
            spur_range_index,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace(
        self, vi, selector_string, timeout, x0, dx, absolute_limit, array_size, actual_array_size
    ):
        """RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace_cfunc is None:
                self.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace"
                )
                self.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace_cfunc(
            vi, selector_string, timeout, x0, dx, absolute_limit, array_size, actual_array_size
        )

    def RFmxSpecAn_SpurFetchRangeSpectrumTrace(
        self, vi, selector_string, timeout, x0, dx, range_spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_SpurFetchRangeSpectrumTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchRangeSpectrumTrace_cfunc is None:
                self.RFmxSpecAn_SpurFetchRangeSpectrumTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchRangeSpectrumTrace"
                )
                self.RFmxSpecAn_SpurFetchRangeSpectrumTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchRangeSpectrumTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchRangeSpectrumTrace_cfunc(
            vi, selector_string, timeout, x0, dx, range_spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_SpurFetchRangeStatusArray(
        self,
        vi,
        selector_string,
        timeout,
        range_status,
        number_of_detected_spurs,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SpurFetchRangeStatusArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchRangeStatusArray_cfunc is None:
                self.RFmxSpecAn_SpurFetchRangeStatusArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchRangeStatusArray"
                )
                self.RFmxSpecAn_SpurFetchRangeStatusArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchRangeStatusArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchRangeStatusArray_cfunc(
            vi,
            selector_string,
            timeout,
            range_status,
            number_of_detected_spurs,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_SpurFetchSpurMeasurementArray(
        self,
        vi,
        selector_string,
        timeout,
        spur_frequency,
        spur_amplitude,
        spur_absolute_limit,
        spur_margin,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SpurFetchSpurMeasurementArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SpurFetchSpurMeasurementArray_cfunc is None:
                self.RFmxSpecAn_SpurFetchSpurMeasurementArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SpurFetchSpurMeasurementArray"
                )
                self.RFmxSpecAn_SpurFetchSpurMeasurementArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SpurFetchSpurMeasurementArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SpurFetchSpurMeasurementArray_cfunc(
            vi,
            selector_string,
            timeout,
            spur_frequency,
            spur_amplitude,
            spur_absolute_limit,
            spur_margin,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchAMToAMTrace(
        self,
        vi,
        selector_string,
        timeout,
        reference_powers,
        measured_am_to_am,
        curve_fit_am_to_am,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_AMPMFetchAMToAMTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchAMToAMTrace_cfunc is None:
                self.RFmxSpecAn_AMPMFetchAMToAMTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchAMToAMTrace"
                )
                self.RFmxSpecAn_AMPMFetchAMToAMTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchAMToAMTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchAMToAMTrace_cfunc(
            vi,
            selector_string,
            timeout,
            reference_powers,
            measured_am_to_am,
            curve_fit_am_to_am,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchAMToPMTrace(
        self,
        vi,
        selector_string,
        timeout,
        reference_powers,
        measured_am_to_pm,
        curve_fit_am_to_pm,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_AMPMFetchAMToPMTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchAMToPMTrace_cfunc is None:
                self.RFmxSpecAn_AMPMFetchAMToPMTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchAMToPMTrace"
                )
                self.RFmxSpecAn_AMPMFetchAMToPMTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchAMToPMTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchAMToPMTrace_cfunc(
            vi,
            selector_string,
            timeout,
            reference_powers,
            measured_am_to_pm,
            curve_fit_am_to_pm,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchCompressionPoints(
        self,
        vi,
        selector_string,
        timeout,
        input_compression_point,
        output_compression_point,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_AMPMFetchCompressionPoints."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchCompressionPoints_cfunc is None:
                self.RFmxSpecAn_AMPMFetchCompressionPoints_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchCompressionPoints"
                )
                self.RFmxSpecAn_AMPMFetchCompressionPoints_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchCompressionPoints_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchCompressionPoints_cfunc(
            vi,
            selector_string,
            timeout,
            input_compression_point,
            output_compression_point,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchCurveFitCoefficients(
        self,
        vi,
        selector_string,
        timeout,
        am_to_am_coefficients,
        am_to_pm_coefficients,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_AMPMFetchCurveFitCoefficients."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchCurveFitCoefficients_cfunc is None:
                self.RFmxSpecAn_AMPMFetchCurveFitCoefficients_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchCurveFitCoefficients"
                )
                self.RFmxSpecAn_AMPMFetchCurveFitCoefficients_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchCurveFitCoefficients_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchCurveFitCoefficients_cfunc(
            vi,
            selector_string,
            timeout,
            am_to_am_coefficients,
            am_to_pm_coefficients,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        processed_mean_acquired_waveform,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform_cfunc is None:
                self.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform")
                )
                self.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            processed_mean_acquired_waveform,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchProcessedReferenceWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        processed_reference_waveform,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_AMPMFetchProcessedReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_AMPMFetchProcessedReferenceWaveform")
                )
                self.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            processed_reference_waveform,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_AMPMFetchRelativePhaseTrace(
        self, vi, selector_string, timeout, x0, dx, relative_phase, array_size, actual_array_size
    ):
        """RFmxSpecAn_AMPMFetchRelativePhaseTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchRelativePhaseTrace_cfunc is None:
                self.RFmxSpecAn_AMPMFetchRelativePhaseTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchRelativePhaseTrace"
                )
                self.RFmxSpecAn_AMPMFetchRelativePhaseTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchRelativePhaseTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchRelativePhaseTrace_cfunc(
            vi, selector_string, timeout, x0, dx, relative_phase, array_size, actual_array_size
        )

    def RFmxSpecAn_AMPMFetchRelativePowerTrace(
        self, vi, selector_string, timeout, x0, dx, relative_power, array_size, actual_array_size
    ):
        """RFmxSpecAn_AMPMFetchRelativePowerTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_AMPMFetchRelativePowerTrace_cfunc is None:
                self.RFmxSpecAn_AMPMFetchRelativePowerTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_AMPMFetchRelativePowerTrace"
                )
                self.RFmxSpecAn_AMPMFetchRelativePowerTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_AMPMFetchRelativePowerTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AMPMFetchRelativePowerTrace_cfunc(
            vi, selector_string, timeout, x0, dx, relative_power, array_size, actual_array_size
        )

    def RFmxSpecAn_DPDFetchDPDPolynomial(
        self, vi, selector_string, timeout, dpd_polynomial, array_size, actual_array_size
    ):
        """RFmxSpecAn_DPDFetchDPDPolynomial."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchDPDPolynomial_cfunc is None:
                self.RFmxSpecAn_DPDFetchDPDPolynomial_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDFetchDPDPolynomial"
                )
                self.RFmxSpecAn_DPDFetchDPDPolynomial_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_DPDFetchDPDPolynomial_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchDPDPolynomial_cfunc(
            vi, selector_string, timeout, dpd_polynomial, array_size, actual_array_size
        )

    def RFmxSpecAn_DPDFetchDVRModel(
        self, vi, selector_string, timeout, dvr_model, array_size, actual_array_size
    ):
        """RFmxSpecAn_DPDFetchDVRModel."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchDVRModel_cfunc is None:
                self.RFmxSpecAn_DPDFetchDVRModel_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDFetchDVRModel"
                )
                self.RFmxSpecAn_DPDFetchDVRModel_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_DPDFetchDVRModel_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchDVRModel_cfunc(
            vi, selector_string, timeout, dvr_model, array_size, actual_array_size
        )

    def RFmxSpecAn_DPDFetchLookupTable(
        self,
        vi,
        selector_string,
        timeout,
        input_powers,
        complex_gains,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_DPDFetchLookupTable."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchLookupTable_cfunc is None:
                self.RFmxSpecAn_DPDFetchLookupTable_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDFetchLookupTable"
                )
                self.RFmxSpecAn_DPDFetchLookupTable_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_DPDFetchLookupTable_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchLookupTable_cfunc(
            vi, selector_string, timeout, input_powers, complex_gains, array_size, actual_array_size
        )

    def RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        processed_mean_acquired_waveform,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform_cfunc is None:
                self.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform")
                )
                self.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            processed_mean_acquired_waveform,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_DPDFetchProcessedReferenceWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        processed_reference_waveform,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_DPDFetchProcessedReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDFetchProcessedReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_DPDFetchProcessedReferenceWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_DPDFetchProcessedReferenceWaveform")
                )
                self.RFmxSpecAn_DPDFetchProcessedReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_DPDFetchProcessedReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDFetchProcessedReferenceWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            processed_reference_waveform,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_ACPFetchAbsolutePowersTrace(
        self,
        vi,
        selector_string,
        timeout,
        trace_index,
        x0,
        dx,
        absolute_powers_trace,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_ACPFetchAbsolutePowersTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchAbsolutePowersTrace_cfunc is None:
                self.RFmxSpecAn_ACPFetchAbsolutePowersTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchAbsolutePowersTrace"
                )
                self.RFmxSpecAn_ACPFetchAbsolutePowersTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_ACPFetchAbsolutePowersTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchAbsolutePowersTrace_cfunc(
            vi,
            selector_string,
            timeout,
            trace_index,
            x0,
            dx,
            absolute_powers_trace,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_ACPFetchOffsetMeasurementArray(
        self,
        vi,
        selector_string,
        timeout,
        lower_relative_power,
        upper_relative_power,
        lower_absolute_power,
        upper_absolute_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_ACPFetchOffsetMeasurementArray."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchOffsetMeasurementArray_cfunc is None:
                self.RFmxSpecAn_ACPFetchOffsetMeasurementArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchOffsetMeasurementArray"
                )
                self.RFmxSpecAn_ACPFetchOffsetMeasurementArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_ACPFetchOffsetMeasurementArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchOffsetMeasurementArray_cfunc(
            vi,
            selector_string,
            timeout,
            lower_relative_power,
            upper_relative_power,
            lower_absolute_power,
            upper_absolute_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_ACPFetchRelativePowersTrace(
        self,
        vi,
        selector_string,
        timeout,
        trace_index,
        x0,
        dx,
        relative_powers_trace,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_ACPFetchRelativePowersTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchRelativePowersTrace_cfunc is None:
                self.RFmxSpecAn_ACPFetchRelativePowersTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchRelativePowersTrace"
                )
                self.RFmxSpecAn_ACPFetchRelativePowersTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_ACPFetchRelativePowersTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchRelativePowersTrace_cfunc(
            vi,
            selector_string,
            timeout,
            trace_index,
            x0,
            dx,
            relative_powers_trace,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_ACPFetchSpectrum(
        self, vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_ACPFetchSpectrum."""
        with self._func_lock:
            if self.RFmxSpecAn_ACPFetchSpectrum_cfunc is None:
                self.RFmxSpecAn_ACPFetchSpectrum_cfunc = self._get_library_function(
                    "RFmxSpecAn_ACPFetchSpectrum"
                )
                self.RFmxSpecAn_ACPFetchSpectrum_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_ACPFetchSpectrum_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ACPFetchSpectrum_cfunc(
            vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        gaussian_probabilities,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace_cfunc is None:
                self.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace_cfunc = (
                    self._get_library_function("RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace")
                )
                self.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            gaussian_probabilities,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_CCDFFetchProbabilitiesTrace(
        self, vi, selector_string, timeout, x0, dx, probabilities, array_size, actual_array_size
    ):
        """RFmxSpecAn_CCDFFetchProbabilitiesTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_CCDFFetchProbabilitiesTrace_cfunc is None:
                self.RFmxSpecAn_CCDFFetchProbabilitiesTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_CCDFFetchProbabilitiesTrace"
                )
                self.RFmxSpecAn_CCDFFetchProbabilitiesTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CCDFFetchProbabilitiesTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CCDFFetchProbabilitiesTrace_cfunc(
            vi, selector_string, timeout, x0, dx, probabilities, array_size, actual_array_size
        )

    def RFmxSpecAn_CHPFetchSpectrum(
        self, vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_CHPFetchSpectrum."""
        with self._func_lock:
            if self.RFmxSpecAn_CHPFetchSpectrum_cfunc is None:
                self.RFmxSpecAn_CHPFetchSpectrum_cfunc = self._get_library_function(
                    "RFmxSpecAn_CHPFetchSpectrum"
                )
                self.RFmxSpecAn_CHPFetchSpectrum_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_CHPFetchSpectrum_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CHPFetchSpectrum_cfunc(
            vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_HarmFetchHarmonicPowerTrace(
        self, vi, selector_string, timeout, x0, dx, power, array_size, actual_array_size
    ):
        """RFmxSpecAn_HarmFetchHarmonicPowerTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmFetchHarmonicPowerTrace_cfunc is None:
                self.RFmxSpecAn_HarmFetchHarmonicPowerTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_HarmFetchHarmonicPowerTrace"
                )
                self.RFmxSpecAn_HarmFetchHarmonicPowerTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_HarmFetchHarmonicPowerTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmFetchHarmonicPowerTrace_cfunc(
            vi, selector_string, timeout, x0, dx, power, array_size, actual_array_size
        )

    def RFmxSpecAn_HarmFetchHarmonicMeasurementArray(
        self,
        vi,
        selector_string,
        timeout,
        average_relative_power,
        average_absolute_power,
        rbw,
        frequency,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_HarmFetchHarmonicMeasurementArray."""
        with self._func_lock:
            if self.RFmxSpecAn_HarmFetchHarmonicMeasurementArray_cfunc is None:
                self.RFmxSpecAn_HarmFetchHarmonicMeasurementArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_HarmFetchHarmonicMeasurementArray")
                )
                self.RFmxSpecAn_HarmFetchHarmonicMeasurementArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_HarmFetchHarmonicMeasurementArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_HarmFetchHarmonicMeasurementArray_cfunc(
            vi,
            selector_string,
            timeout,
            average_relative_power,
            average_absolute_power,
            rbw,
            frequency,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_SEMFetchAbsoluteMaskTrace(
        self, vi, selector_string, timeout, x0, dx, absolute_mask, array_size, actual_array_size
    ):
        """RFmxSpecAn_SEMFetchAbsoluteMaskTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchAbsoluteMaskTrace_cfunc is None:
                self.RFmxSpecAn_SEMFetchAbsoluteMaskTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchAbsoluteMaskTrace"
                )
                self.RFmxSpecAn_SEMFetchAbsoluteMaskTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchAbsoluteMaskTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchAbsoluteMaskTrace_cfunc(
            vi, selector_string, timeout, x0, dx, absolute_mask, array_size, actual_array_size
        )

    def RFmxSpecAn_SEMFetchLowerOffsetMarginArray(
        self,
        vi,
        selector_string,
        timeout,
        measurement_status,
        margin,
        margin_frequency,
        margin_absolute_power,
        margin_relative_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SEMFetchLowerOffsetMarginArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchLowerOffsetMarginArray_cfunc is None:
                self.RFmxSpecAn_SEMFetchLowerOffsetMarginArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchLowerOffsetMarginArray"
                )
                self.RFmxSpecAn_SEMFetchLowerOffsetMarginArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchLowerOffsetMarginArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchLowerOffsetMarginArray_cfunc(
            vi,
            selector_string,
            timeout,
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_SEMFetchLowerOffsetPowerArray(
        self,
        vi,
        selector_string,
        timeout,
        total_absolute_power,
        total_relative_power,
        peak_absolute_power,
        peak_frequency,
        peak_relative_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SEMFetchLowerOffsetPowerArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchLowerOffsetPowerArray_cfunc is None:
                self.RFmxSpecAn_SEMFetchLowerOffsetPowerArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchLowerOffsetPowerArray"
                )
                self.RFmxSpecAn_SEMFetchLowerOffsetPowerArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchLowerOffsetPowerArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchLowerOffsetPowerArray_cfunc(
            vi,
            selector_string,
            timeout,
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_SEMFetchRelativeMaskTrace(
        self, vi, selector_string, timeout, x0, dx, relative_mask, array_size, actual_array_size
    ):
        """RFmxSpecAn_SEMFetchRelativeMaskTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchRelativeMaskTrace_cfunc is None:
                self.RFmxSpecAn_SEMFetchRelativeMaskTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchRelativeMaskTrace"
                )
                self.RFmxSpecAn_SEMFetchRelativeMaskTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchRelativeMaskTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchRelativeMaskTrace_cfunc(
            vi, selector_string, timeout, x0, dx, relative_mask, array_size, actual_array_size
        )

    def RFmxSpecAn_SEMFetchSpectrum(
        self, vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_SEMFetchSpectrum."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchSpectrum_cfunc is None:
                self.RFmxSpecAn_SEMFetchSpectrum_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchSpectrum"
                )
                self.RFmxSpecAn_SEMFetchSpectrum_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchSpectrum_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchSpectrum_cfunc(
            vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_SEMFetchUpperOffsetMarginArray(
        self,
        vi,
        selector_string,
        timeout,
        measurement_status,
        margin,
        margin_frequency,
        margin_absolute_power,
        margin_relative_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SEMFetchUpperOffsetMarginArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchUpperOffsetMarginArray_cfunc is None:
                self.RFmxSpecAn_SEMFetchUpperOffsetMarginArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchUpperOffsetMarginArray"
                )
                self.RFmxSpecAn_SEMFetchUpperOffsetMarginArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchUpperOffsetMarginArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchUpperOffsetMarginArray_cfunc(
            vi,
            selector_string,
            timeout,
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_SEMFetchUpperOffsetPowerArray(
        self,
        vi,
        selector_string,
        timeout,
        total_absolute_power,
        total_relative_power,
        peak_absolute_power,
        peak_frequency,
        peak_relative_power,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_SEMFetchUpperOffsetPowerArray."""
        with self._func_lock:
            if self.RFmxSpecAn_SEMFetchUpperOffsetPowerArray_cfunc is None:
                self.RFmxSpecAn_SEMFetchUpperOffsetPowerArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_SEMFetchUpperOffsetPowerArray"
                )
                self.RFmxSpecAn_SEMFetchUpperOffsetPowerArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_SEMFetchUpperOffsetPowerArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SEMFetchUpperOffsetPowerArray_cfunc(
            vi,
            selector_string,
            timeout,
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_OBWFetchSpectrumTrace(
        self, vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
    ):
        """RFmxSpecAn_OBWFetchSpectrumTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_OBWFetchSpectrumTrace_cfunc is None:
                self.RFmxSpecAn_OBWFetchSpectrumTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_OBWFetchSpectrumTrace"
                )
                self.RFmxSpecAn_OBWFetchSpectrumTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_OBWFetchSpectrumTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_OBWFetchSpectrumTrace_cfunc(
            vi, selector_string, timeout, x0, dx, spectrum, array_size, actual_array_size
        )

    def RFmxSpecAn_TXPFetchPowerTrace(
        self, vi, selector_string, timeout, x0, dx, power, array_size, actual_array_size
    ):
        """RFmxSpecAn_TXPFetchPowerTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_TXPFetchPowerTrace_cfunc is None:
                self.RFmxSpecAn_TXPFetchPowerTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_TXPFetchPowerTrace"
                )
                self.RFmxSpecAn_TXPFetchPowerTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_TXPFetchPowerTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_TXPFetchPowerTrace_cfunc(
            vi, selector_string, timeout, x0, dx, power, array_size, actual_array_size
        )

    def RFmxSpecAn_IQFetchData(
        self,
        vi,
        selector_string,
        timeout,
        record_to_fetch,
        samples_to_read,
        t0,
        dt,
        data,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IQFetchData."""
        with self._func_lock:
            if self.RFmxSpecAn_IQFetchData_cfunc is None:
                self.RFmxSpecAn_IQFetchData_cfunc = self._get_library_function(
                    "RFmxSpecAn_IQFetchData"
                )
                self.RFmxSpecAn_IQFetchData_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_int64,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IQFetchData_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IQFetchData_cfunc(
            vi,
            selector_string,
            timeout,
            record_to_fetch,
            samples_to_read,
            t0,
            dt,
            data,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PhaseNoiseFetchIntegratedNoise(
        self,
        vi,
        selector_string,
        timeout,
        integrated_phase_noise,
        residual_pm_in_radian,
        residual_pm_in_degree,
        residual_fm,
        jitter,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_PhaseNoiseFetchIntegratedNoise."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseFetchIntegratedNoise"
                )
                self.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise_cfunc(
            vi,
            selector_string,
            timeout,
            integrated_phase_noise,
            residual_pm_in_radian,
            residual_pm_in_degree,
            residual_fm,
            jitter,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace(
        self,
        vi,
        selector_string,
        timeout,
        frequency,
        measured_phase_noise,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace_cfunc = (
                    self._get_library_function("RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace")
                )
                self.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace_cfunc(
            vi,
            selector_string,
            timeout,
            frequency,
            measured_phase_noise,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace(
        self,
        vi,
        selector_string,
        timeout,
        frequency,
        smoothed_phase_noise,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace_cfunc = (
                    self._get_library_function("RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace")
                )
                self.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace_cfunc(
            vi,
            selector_string,
            timeout,
            frequency,
            smoothed_phase_noise,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PhaseNoiseFetchSpotNoise(
        self, vi, selector_string, timeout, spot_phase_noise, array_size, actual_array_size
    ):
        """RFmxSpecAn_PhaseNoiseFetchSpotNoise."""
        with self._func_lock:
            if self.RFmxSpecAn_PhaseNoiseFetchSpotNoise_cfunc is None:
                self.RFmxSpecAn_PhaseNoiseFetchSpotNoise_cfunc = self._get_library_function(
                    "RFmxSpecAn_PhaseNoiseFetchSpotNoise"
                )
                self.RFmxSpecAn_PhaseNoiseFetchSpotNoise_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PhaseNoiseFetchSpotNoise_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PhaseNoiseFetchSpotNoise_cfunc(
            vi, selector_string, timeout, spot_phase_noise, array_size, actual_array_size
        )

    def RFmxSpecAn_PAVTFetchAmplitudeTrace(
        self,
        vi,
        selector_string,
        timeout,
        trace_index,
        x0,
        dx,
        amplitude,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_PAVTFetchAmplitudeTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTFetchAmplitudeTrace_cfunc is None:
                self.RFmxSpecAn_PAVTFetchAmplitudeTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTFetchAmplitudeTrace"
                )
                self.RFmxSpecAn_PAVTFetchAmplitudeTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PAVTFetchAmplitudeTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTFetchAmplitudeTrace_cfunc(
            vi,
            selector_string,
            timeout,
            trace_index,
            x0,
            dx,
            amplitude,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray(
        self,
        vi,
        selector_string,
        timeout,
        mean_relative_phase,
        mean_relative_amplitude,
        mean_absolute_phase,
        mean_absolute_amplitude,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray_cfunc is None:
                self.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray"
                )
                self.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray_cfunc(
            vi,
            selector_string,
            timeout,
            mean_relative_phase,
            mean_relative_amplitude,
            mean_absolute_phase,
            mean_absolute_amplitude,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PAVTFetchPhaseTrace(
        self,
        vi,
        selector_string,
        timeout,
        trace_index,
        x0,
        dx,
        phase,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_PAVTFetchPhaseTrace."""
        with self._func_lock:
            if self.RFmxSpecAn_PAVTFetchPhaseTrace_cfunc is None:
                self.RFmxSpecAn_PAVTFetchPhaseTrace_cfunc = self._get_library_function(
                    "RFmxSpecAn_PAVTFetchPhaseTrace"
                )
                self.RFmxSpecAn_PAVTFetchPhaseTrace_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PAVTFetchPhaseTrace_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PAVTFetchPhaseTrace_cfunc(
            vi, selector_string, timeout, trace_index, x0, dx, phase, array_size, actual_array_size
        )

    def RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        processed_mean_acquired_waveform,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform_cfunc is None:
                self.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform")
                )
                self.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            processed_mean_acquired_waveform,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_IDPDFetchProcessedReferenceWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        processed_reference_waveform,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IDPDFetchProcessedReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_IDPDFetchProcessedReferenceWaveform")
                )
                self.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            processed_reference_waveform,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_IDPDFetchPredistortedWaveform(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        predistorted_waveform,
        papr,
        power_offset,
        gain,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IDPDFetchPredistortedWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDFetchPredistortedWaveform_cfunc is None:
                self.RFmxSpecAn_IDPDFetchPredistortedWaveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_IDPDFetchPredistortedWaveform"
                )
                self.RFmxSpecAn_IDPDFetchPredistortedWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IDPDFetchPredistortedWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDFetchPredistortedWaveform_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            predistorted_waveform,
            papr,
            power_offset,
            gain,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_IDPDFetchEqualizerCoefficients(
        self,
        vi,
        selector_string,
        timeout,
        x0,
        dx,
        equalizer_coefficients,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IDPDFetchEqualizerCoefficients."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDFetchEqualizerCoefficients_cfunc is None:
                self.RFmxSpecAn_IDPDFetchEqualizerCoefficients_cfunc = self._get_library_function(
                    "RFmxSpecAn_IDPDFetchEqualizerCoefficients"
                )
                self.RFmxSpecAn_IDPDFetchEqualizerCoefficients_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IDPDFetchEqualizerCoefficients_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDFetchEqualizerCoefficients_cfunc(
            vi,
            selector_string,
            timeout,
            x0,
            dx,
            equalizer_coefficients,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_IDPDGetEqualizerReferenceWaveform(
        self,
        vi,
        selector_string,
        x0,
        dx,
        equalizer_reference_waveform,
        papr,
        array_size,
        actual_array_size,
    ):
        """RFmxSpecAn_IDPDGetEqualizerReferenceWaveform."""
        with self._func_lock:
            if self.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform_cfunc is None:
                self.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform_cfunc = (
                    self._get_library_function("RFmxSpecAn_IDPDGetEqualizerReferenceWaveform")
                )
                self.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform_cfunc(
            vi,
            selector_string,
            x0,
            dx,
            equalizer_reference_waveform,
            papr,
            array_size,
            actual_array_size,
        )

    def RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray(
        self, vi, selector_string, timeout, mean_absolute_power, array_size, actual_array_size
    ):
        """RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray_cfunc is None:
                self.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray_cfunc = (
                    self._get_library_function("RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray")
                )
                self.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray_cfunc(
            vi, selector_string, timeout, mean_absolute_power, array_size, actual_array_size
        )

    def RFmxSpecAn_PowerListFetchMaximumPowerArray(
        self, vi, selector_string, timeout, maximum_power, array_size, actual_array_size
    ):
        """RFmxSpecAn_PowerListFetchMaximumPowerArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PowerListFetchMaximumPowerArray_cfunc is None:
                self.RFmxSpecAn_PowerListFetchMaximumPowerArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_PowerListFetchMaximumPowerArray"
                )
                self.RFmxSpecAn_PowerListFetchMaximumPowerArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PowerListFetchMaximumPowerArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PowerListFetchMaximumPowerArray_cfunc(
            vi, selector_string, timeout, maximum_power, array_size, actual_array_size
        )

    def RFmxSpecAn_PowerListFetchMinimumPowerArray(
        self, vi, selector_string, timeout, minimum_power, array_size, actual_array_size
    ):
        """RFmxSpecAn_PowerListFetchMinimumPowerArray."""
        with self._func_lock:
            if self.RFmxSpecAn_PowerListFetchMinimumPowerArray_cfunc is None:
                self.RFmxSpecAn_PowerListFetchMinimumPowerArray_cfunc = self._get_library_function(
                    "RFmxSpecAn_PowerListFetchMinimumPowerArray"
                )
                self.RFmxSpecAn_PowerListFetchMinimumPowerArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_PowerListFetchMinimumPowerArray_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_PowerListFetchMinimumPowerArray_cfunc(
            vi, selector_string, timeout, minimum_power, array_size, actual_array_size
        )

    def RFmxSpecAn_CloneSignalConfiguration(self, vi, old_signal_name, new_signal_name):
        """RFmxSpecAn_CloneSignalConfiguration."""
        with self._func_lock:
            if self.RFmxSpecAn_CloneSignalConfiguration_cfunc is None:
                self.RFmxSpecAn_CloneSignalConfiguration_cfunc = self._get_library_function(
                    "RFmxSpecAn_CloneSignalConfiguration"
                )
                self.RFmxSpecAn_CloneSignalConfiguration_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_CloneSignalConfiguration_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_CloneSignalConfiguration_cfunc(vi, old_signal_name, new_signal_name)

    def RFmxSpecAn_DeleteSignalConfiguration(self, vi, signal_name):
        """RFmxSpecAn_DeleteSignalConfiguration."""
        with self._func_lock:
            if self.RFmxSpecAn_DeleteSignalConfiguration_cfunc is None:
                self.RFmxSpecAn_DeleteSignalConfiguration_cfunc = self._get_library_function(
                    "RFmxSpecAn_DeleteSignalConfiguration"
                )
                self.RFmxSpecAn_DeleteSignalConfiguration_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_DeleteSignalConfiguration_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DeleteSignalConfiguration_cfunc(vi, signal_name)

    def RFmxSpecAn_SendSoftwareEdgeTrigger(self, vi):
        """RFmxSpecAn_SendSoftwareEdgeTrigger."""
        with self._func_lock:
            if self.RFmxSpecAn_SendSoftwareEdgeTrigger_cfunc is None:
                self.RFmxSpecAn_SendSoftwareEdgeTrigger_cfunc = self._get_library_function(
                    "RFmxSpecAn_SendSoftwareEdgeTrigger"
                )
                self.RFmxSpecAn_SendSoftwareEdgeTrigger_cfunc.argtypes = [ctypes.c_uint32]
                self.RFmxSpecAn_SendSoftwareEdgeTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_SendSoftwareEdgeTrigger_cfunc(vi)

    def RFmxSpecAn_GetAllNamedResultNames(
        self,
        vi,
        selector_string,
        result_names,
        result_names_buffer_size,
        actual_result_names_size,
        default_result_exists,
    ):
        """RFmxSpecAn_GetAllNamedResultNames."""
        with self._func_lock:
            if self.RFmxSpecAn_GetAllNamedResultNames_cfunc is None:
                self.RFmxSpecAn_GetAllNamedResultNames_cfunc = self._get_library_function(
                    "RFmxSpecAn_GetAllNamedResultNames"
                )
                self.RFmxSpecAn_GetAllNamedResultNames_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxSpecAn_GetAllNamedResultNames_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_GetAllNamedResultNames_cfunc(
            vi,
            selector_string,
            result_names,
            result_names_buffer_size,
            actual_result_names_size,
            default_result_exists,
        )

    def RFmxSpecAn_DPDApplyDigitalPredistortion(
        self,
        vi,
        selector_string,
        x0_in,
        dx_in,
        waveform_in,
        array_size_in,
        idle_duration_present,
        measurement_timeout,
        x0_out,
        dx_out,
        waveform_out,
        array_size_out,
        actual_array_size_out,
        papr,
        power_offset,
    ):
        """RFmxSpecAn_DPDApplyDigitalPredistortion."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDApplyDigitalPredistortion_cfunc is None:
                self.RFmxSpecAn_DPDApplyDigitalPredistortion_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDApplyDigitalPredistortion"
                )
                self.RFmxSpecAn_DPDApplyDigitalPredistortion_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_DPDApplyDigitalPredistortion_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDApplyDigitalPredistortion_cfunc(
            vi,
            selector_string,
            x0_in,
            dx_in,
            waveform_in,
            array_size_in,
            idle_duration_present,
            measurement_timeout,
            x0_out,
            dx_out,
            waveform_out,
            array_size_out,
            actual_array_size_out,
            papr,
            power_offset,
        )

    def RFmxSpecAn_DPDApplyPreDPDSignalConditioning(
        self,
        vi,
        selector_string,
        x0_in,
        dx_in,
        waveform_in,
        array_size_in,
        idle_duration_present,
        x0_out,
        dx_out,
        waveform_out,
        array_size_out,
        actual_array_size_out,
        papr,
    ):
        """RFmxSpecAn_DPDApplyPreDPDSignalConditioning."""
        with self._func_lock:
            if self.RFmxSpecAn_DPDApplyPreDPDSignalConditioning_cfunc is None:
                self.RFmxSpecAn_DPDApplyPreDPDSignalConditioning_cfunc = self._get_library_function(
                    "RFmxSpecAn_DPDApplyPreDPDSignalConditioning"
                )
                self.RFmxSpecAn_DPDApplyPreDPDSignalConditioning_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxSpecAn_DPDApplyPreDPDSignalConditioning_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_DPDApplyPreDPDSignalConditioning_cfunc(
            vi,
            selector_string,
            x0_in,
            dx_in,
            waveform_in,
            array_size_in,
            idle_duration_present,
            x0_out,
            dx_out,
            waveform_out,
            array_size_out,
            actual_array_size_out,
            papr,
        )

    def RFmxSpecAn_ClearNoiseCalibrationDatabase(self, vi, selector_string):
        """RFmxSpecAn_ClearNoiseCalibrationDatabase."""
        with self._func_lock:
            if self.RFmxSpecAn_ClearNoiseCalibrationDatabase_cfunc is None:
                self.RFmxSpecAn_ClearNoiseCalibrationDatabase_cfunc = self._get_library_function(
                    "RFmxSpecAn_ClearNoiseCalibrationDatabase"
                )
                self.RFmxSpecAn_ClearNoiseCalibrationDatabase_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxSpecAn_ClearNoiseCalibrationDatabase_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_ClearNoiseCalibrationDatabase_cfunc(vi, selector_string)

    def RFmxSpecAn_AnalyzeIQ1Waveform(
        self, vi, selector_string, result_name, x0, dx, iq, array_size, reset, reserved
    ):
        """RFmxSpecAn_AnalyzeIQ1Waveform."""
        with self._func_lock:
            if self.RFmxSpecAn_AnalyzeIQ1Waveform_cfunc is None:
                self.RFmxSpecAn_AnalyzeIQ1Waveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_AnalyzeIQ1Waveform"
                )
                self.RFmxSpecAn_AnalyzeIQ1Waveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int64,
                ]
                self.RFmxSpecAn_AnalyzeIQ1Waveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AnalyzeIQ1Waveform_cfunc(
            vi, selector_string, result_name, x0, dx, iq, array_size, reset, reserved
        )

    def RFmxSpecAn_AnalyzeSpectrum1Waveform(
        self, vi, selector_string, result_name, x0, dx, spectrum, array_size, reset, reserved
    ):
        """RFmxSpecAn_AnalyzeSpectrum1Waveform."""
        with self._func_lock:
            if self.RFmxSpecAn_AnalyzeSpectrum1Waveform_cfunc is None:
                self.RFmxSpecAn_AnalyzeSpectrum1Waveform_cfunc = self._get_library_function(
                    "RFmxSpecAn_AnalyzeSpectrum1Waveform"
                )
                self.RFmxSpecAn_AnalyzeSpectrum1Waveform_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int64,
                ]
                self.RFmxSpecAn_AnalyzeSpectrum1Waveform_cfunc.restype = ctypes.c_int32
        return self.RFmxSpecAn_AnalyzeSpectrum1Waveform_cfunc(
            vi, selector_string, result_name, x0, dx, spectrum, array_size, reset, reserved
        )
