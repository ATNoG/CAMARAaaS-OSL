{
java.util.HashMap<String,String> charvals = new java.util.HashMap<>();
charvals.put("_CR_SPEC",String.format("""
apiVersion: av.it.pt/v1
kind: UEQoDProfile
metadata:
  name: ue-qod-profile-init
spec:
  ITAvSliceManager:
    slice: %s
    defaultProfile:
      AMBRUP: %s
      AMBRDW: %s
    profiles: %s
  qodProv:
    operation: %s
    provisioningId: %s
    device:
      phoneNumber: %s
      networkAccessIdentifier: %s
      ipv4Address:
        publicAddress: %s
        privateAddress: %s
        publicPort: %s
      ipv6Address: %s
    qosProfile: %s
    sink: %s
    sinkCredential:
        credentialType: %s
"""
, getCharValAsString("ITAvSliceManager.slice"), getCharValAsString("ITAvSliceManager.defaultProfile.AMBRUP"), getCharValAsString("ITAvSliceManager.defaultProfile.AMBRDW"), getCharValAsString("ITAvSliceManager.profiles"), getCharValAsString("qodProv.operation"), getCharValAsString("qodProv.provisioningId"), getCharValAsString("qodProv.device.phoneNumber"), getCharValAsString("qodProv.device.networkAccessIdentifier"), getCharValAsString("qodProv.device.ipv4Address.publicAddress"), getCharValAsString("qodProv.device.ipv4Address.privateAddress"), getCharValAsString("qodProv.device.ipv4Address.publicPort"), getCharValAsString("qodProv.device.ipv6Address"), getCharValAsString("qodProv.qosProfile"), getCharValAsString("qodProv.sink"), getCharValAsString("qodProv.sinkCredential.credentialType")));
setServiceRefCharacteristicsValues("UE QoD Profile Enforcer (RFS)", charvals);
}
setCharValFromStringType("camaraResults", getServiceRefPropValue("UE QoD Profile Enforcer (RFS)", "serviceCharacteristicValue", "spec.camaraResults"));
