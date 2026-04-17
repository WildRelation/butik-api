package se.kth.datalake.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import se.kth.datalake.service.DatalakeService;

@Controller
public class DatasetController {

    private final DatalakeService service;

    public DatasetController(DatalakeService service) {
        this.service = service;
    }

    @GetMapping("/")
    public String index(Model model, @RequestParam(defaultValue = "") String q) {
        try {
            var datasets = service.hamtaDatasets();
            if (!q.isEmpty()) {
                datasets = datasets.stream()
                    .filter(d -> d.getNamn().toLowerCase().contains(q.toLowerCase())
                              || d.getBeskrivning().toLowerCase().contains(q.toLowerCase()))
                    .toList();
            }
            model.addAttribute("datasets", datasets);
            model.addAttribute("q", q);
        } catch (Exception e) {
            model.addAttribute("fel", "Kunde inte nå datalaken: " + e.getMessage());
        }
        return "index";
    }

    @GetMapping("/dataset/{namn}")
    public String dataset(@PathVariable String namn, Model model) {
        try {
            model.addAttribute("dataset", service.hamtaDataset(namn));
        } catch (Exception e) {
            model.addAttribute("fel", "Kunde inte hämta dataset: " + e.getMessage());
        }
        return "dataset";
    }

    @GetMapping("/upload")
    public String uploadForm() {
        return "upload";
    }

    @PostMapping("/upload")
    public String upload(@RequestParam MultipartFile fil,
                         @RequestParam String tabellnamn,
                         RedirectAttributes attrs) {
        try {
            service.laddaUpp(fil, tabellnamn);
            attrs.addFlashAttribute("success", "Dataset '" + tabellnamn + "' laddades upp!");
            return "redirect:/dataset/" + tabellnamn;
        } catch (Exception e) {
            attrs.addFlashAttribute("fel", "Uppladdning misslyckades: " + e.getMessage());
            return "redirect:/upload";
        }
    }
}
