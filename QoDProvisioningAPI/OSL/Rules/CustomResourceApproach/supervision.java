{
java.util.HashMap<String,String> charvals = new java.util.HashMap<>();
charvals.put("_CR_SPEC",String.format("""
apiVersion: av.it.pt/v1
kind: CAMARAaaS-QoDProvisiongAPI
metadata:
  name: _to_replace_
spec:
  messageBroker:
    address: "%s"
    port: %d
    username: "%s"
    password: "%s"
  serviceUnderControl:
    uuid: "%s"
"""
, getCharValAsString("messageBroker.address"), getCharValNumber("messageBroker.port"), getCharValAsString("messageBroker.username"), getCharValAsString("messageBroker.password"), getCharValAsString("serviceUnderControl.uuid")));
setServiceRefCharacteristicsValues("CAMARAaaS - QoD Provisioning API CR (RFS)", charvals);
}
setCharValFromStringType("camaraAPI.status", getServiceRefPropValue("CAMARAaaS - QoD Provisioning API CR (RFS)", "serviceCharacteristicValue", "spec.camaraAPI.status"));
setCharValFromStringType("camaraAPI.url", getServiceRefPropValue("CAMARAaaS - QoD Provisioning API CR (RFS)", "serviceCharacteristicValue", "spec.camaraAPI.url"));
setCharValFromStringType("camaraAPI.username", getServiceRefPropValue("CAMARAaaS - QoD Provisioning API CR (RFS)", "serviceCharacteristicValue", "spec.camaraAPI.username"));
setCharValFromStringType("camaraAPI.password", getServiceRefPropValue("CAMARAaaS - QoD Provisioning API CR (RFS)", "serviceCharacteristicValue", "spec.camaraAPI.password"));
