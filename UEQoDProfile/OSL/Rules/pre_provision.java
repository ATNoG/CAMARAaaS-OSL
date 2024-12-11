{
java.util.HashMap<String,String> charvals = new java.util.HashMap<>();
charvals.put("_CR_SPEC",String.format("""
apiVersion: av.it.pt/v1
kind: UEQoDProfile
metadata:
  name: _to_replace_
spec:
  qodProv:
    device:
      phoneNumber: "%s"
      networkAccessIdentifier: "%s"
      ipv4Address:
        publicAddress: "%s"
        privateAddress: "%s"
        privatePort: "%s"
      ipv6Address: "%s"
    qosProfile: "%s"
    sink: "%s"
    sinkCredential:
      credentialType: "%s"
  camaraLastRequest: "%s"
"""
, getCharValAsString("qodProv.device.phoneNumber"), getCharValAsString("qodProv.device.networkAccessIdentifier"), getCharValAsString("qodProv.device.ipv4Address.publicAddress"), getCharValAsString("qodProv.device.ipv4Address.privateAddress"), getCharValAsString("qodProv.device.ipv4Address.privatePort"), getCharValAsString("qodProv.device.ipv6Address"), getCharValAsString("qodProv.qosProfile"), getCharValAsString("qodProv.sink"), getCharValAsString("qodProv.sinkCredential.credentialType"), getCharValAsString("camaraLastRequest")));
setServiceRefCharacteristicsValues("CAMARAaaS - UE Profile Enforcer (RFS)", charvals);
}
