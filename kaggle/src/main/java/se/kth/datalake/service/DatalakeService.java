package se.kth.datalake.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import se.kth.datalake.model.Dataset;
import se.kth.datalake.model.DatasetDetalj;

import java.util.Arrays;
import java.util.List;

@Service
public class DatalakeService {

    @Value("${datalake.url}")
    private String datalakeUrl;

    @Value("${datalake.apikey}")
    private String apiKey;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper mapper = new ObjectMapper();

    public List<Dataset> hamtaDatasets() {
        Dataset[] datasets = restTemplate.getForObject(
            datalakeUrl + "/api/datasets", Dataset[].class
        );
        return datasets != null ? Arrays.asList(datasets) : List.of();
    }

    public DatasetDetalj hamtaDataset(String namn) {
        return restTemplate.getForObject(
            datalakeUrl + "/api/datasets/" + namn, DatasetDetalj.class
        );
    }

    public void laddaUpp(MultipartFile fil, String tabellnamn) throws Exception {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        headers.set("X-API-Key", apiKey);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("tabellnamn", tabellnamn);
        body.add("fil", new ByteArrayResource(fil.getBytes()) {
            @Override
            public String getFilename() { return fil.getOriginalFilename(); }
        });

        HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);
        restTemplate.postForEntity(datalakeUrl + "/api/datasets/upload", request, String.class);
    }
}
