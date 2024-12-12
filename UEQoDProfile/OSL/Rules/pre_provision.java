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
"""
, getCharValAsString("ITAvSliceManager.slice"), getCharValAsString("ITAvSliceManager.defaultProfile.AMBRUP"), getCharValAsString("ITAvSliceManager.defaultProfile.AMBRDW"), getCharValAsString("ITAvSliceManager.profiles")));
setServiceRefCharacteristicsValues("UE QoD Profile Enforcer (RFS)", charvals);
}