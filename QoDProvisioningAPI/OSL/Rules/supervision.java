{
java.util.HashMap<String,String> charvals = new java.util.HashMap<>();
charvals.put("_CR_SPEC",String.format("""
apiVersion: av.it.pt/v1
kind: CAMARAaaS-QoDProvisiongAPI
metadata:
  name: _to_replace_
spec:
  messageBroker:
    url: "%s"
    username: "%s"
    password: "%s"
  serviceUnderControl:
    uuid: "%s"
"""
, getCharValAsString("messageBroker.url"), getCharValAsString("messageBroker.username"), getCharValAsString("messageBroker.password"), getCharValAsString("serviceUnderControl.uuid")));
setServiceRefCharacteristicsValues("CAMARAaaS - QoD Provisioning API (RFS)	", charvals);
}