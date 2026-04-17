package se.kth.datalake.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Dataset {
    private String namn;
    private String beskrivning;

    @JsonProperty("källa")
    private String kalla;

    public String getNamn()        { return namn; }
    public String getBeskrivning() { return beskrivning; }
    public String getKalla()       { return kalla; }

    public void setNamn(String namn)               { this.namn = namn; }
    public void setBeskrivning(String beskrivning) { this.beskrivning = beskrivning; }

    @JsonProperty("källa")
    public void setKalla(String kalla)             { this.kalla = kalla; }
}
