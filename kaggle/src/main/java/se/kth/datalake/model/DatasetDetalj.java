package se.kth.datalake.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class DatasetDetalj {
    private String namn;
    private List<String> kolumner;

    @JsonProperty("antal_rader")
    private int antalRader;

    private List<Map<String, Object>> data;

    public String getNamn()                       { return namn; }
    public List<String> getKolumner()             { return kolumner; }
    public int getAntalRader()                    { return antalRader; }
    public List<Map<String, Object>> getData()    { return data; }

    public void setNamn(String namn)                            { this.namn = namn; }
    public void setKolumner(List<String> kolumner)              { this.kolumner = kolumner; }

    @JsonProperty("antal_rader")
    public void setAntalRader(int antalRader)                   { this.antalRader = antalRader; }
    public void setData(List<Map<String, Object>> data)         { this.data = data; }
}
