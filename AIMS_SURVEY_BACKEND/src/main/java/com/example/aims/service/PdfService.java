package com.example.aims.service;

import com.example.aims.model.Patient;
import com.example.aims.model.Survey;
import com.itextpdf.text.*;
import com.itextpdf.text.pdf.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.servlet.http.HttpServletResponse;
import java.io.OutputStream;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class PdfService {

    @Autowired
    private MlService mlService;

    public void generatePdf(Patient patient, Survey survey, String chartBase64, HttpServletResponse response) {
        try {
            response.setContentType("application/pdf");
            response.setHeader("Content-Disposition",
                    "attachment; filename=AIMS_Survey_Report_" + patient.getFirstName() + "_" + patient.getLastName() + ".pdf");

            Document document = new Document(PageSize.A4, 40, 40, 60, 50);
            OutputStream out = response.getOutputStream();
            PdfWriter.getInstance(document, out);
            document.open();

            addMetaData(document);
            addTitle(document);
            addPatientDetails(document, patient);
            addSurveyTable(document, survey);
            addOtherIssuesSection(document, survey);
            addAssessment(document, survey);
            addChartImage(document, chartBase64);

            document.close();
            out.flush();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void addMetaData(Document document) {
        document.addTitle("AIMS Health Survey");
        document.addAuthor("AIMS System");
        document.addSubject("Survey Report");
        document.addKeywords("AIMS, Health, Survey");
        document.addCreator("AIMS PDF Generator");
    }

    private void addTitle(Document document) throws DocumentException {
        Font titleFont = new Font(Font.FontFamily.HELVETICA, 18, Font.BOLD, BaseColor.BLUE);
        Paragraph title = new Paragraph("AIMS Health Survey Report", titleFont);
        title.setAlignment(Element.ALIGN_CENTER);
        title.setSpacingAfter(20);
        document.add(title);
    }

    private void addPatientDetails(Document document, Patient patient) throws DocumentException {
        Font headerFont = sectionFont();
        Font labelFont = boldFont();
        Font valueFont = normalFont();

        document.add(new Paragraph("Patient Information", headerFont));
        addLabelValue(document, "Name", patient.getFirstName() + " " + patient.getLastName(), labelFont, valueFont);
        addLabelValue(document, "Age", String.valueOf(patient.getAge()), labelFont, valueFont);
        addLabelValue(document, "Gender", patient.getGender(), labelFont, valueFont);
        addLabelValue(document, "Survey Date", String.valueOf(patient.getSurveyDate()), labelFont, valueFont);
        document.add(Chunk.NEWLINE);
    }

    private void addSurveyTable(Document document, Survey survey) throws DocumentException {
        Font labelFont = boldFont();
        Font valueFont = normalFont();

        document.add(new Paragraph("Survey Ratings (1–5)", sectionFont()));
        document.add(Chunk.NEWLINE);

        PdfPTable table = new PdfPTable(2);
        table.setWidthPercentage(100);
        table.setWidths(new int[]{3, 1});

        addTableHeader(table, "Survey Parameter", labelFont);
        addTableHeader(table, "Score", labelFont);

        boolean shaded = false;
        shaded = addStyledRow(table, "Facial Muscles", survey.getFacialMuscles(), valueFont, shaded);
        shaded = addStyledRow(table, "Lips/Perioral", survey.getLipsPerioral(), valueFont, shaded);
        shaded = addStyledRow(table, "Jaw", survey.getJaw(), valueFont, shaded);
        shaded = addStyledRow(table, "Tongue", survey.getTongue(), valueFont, shaded);
        shaded = addStyledRow(table, "Upper Extremities", survey.getUpperExtremities(), valueFont, shaded);
        shaded = addStyledRow(table, "Lower Extremities", survey.getLowerExtremities(), valueFont, shaded);
        shaded = addStyledRow(table, "Neck/Shoulders/Hips", survey.getNeckShouldersHips(), valueFont, shaded);
        shaded = addStyledRow(table, "Severity of Movements", survey.getSeverityOfMovements(), valueFont, shaded);
        shaded = addStyledRow(table, "Incapacitation", survey.getIncapacitationDueToMovements(), valueFont, shaded);
        shaded = addStyledRow(table, "Patient Awareness", survey.getPatientAwareness(), valueFont, shaded);
        shaded = addStyledRow(table, "Emotional Distress", survey.getEmotionalDistress(), valueFont, shaded);
        shaded = addStyledRow(table, "Global Rating", survey.getGlobalRating(), valueFont, shaded);

        document.add(table);
        document.add(Chunk.NEWLINE);
    }

    private void addAssessment(Document document, Survey survey) throws DocumentException {
        Font labelFont = boldFont();
        Font valueFont = normalFont();

        // 🔹 Prepare survey data to send to ML service
        Map<String, Integer> surveyData = new HashMap<>();
        surveyData.put("facialMuscles", survey.getFacialMuscles());
        surveyData.put("lipsPerioral", survey.getLipsPerioral());
        surveyData.put("jaw", survey.getJaw());
        surveyData.put("tongue", survey.getTongue());
        surveyData.put("upperExtremities", survey.getUpperExtremities());
        surveyData.put("lowerExtremities", survey.getLowerExtremities());
        surveyData.put("neckShouldersHips", survey.getNeckShouldersHips());
        surveyData.put("severityOfMovements", survey.getSeverityOfMovements());
        surveyData.put("incapacitationDueToMovements", survey.getIncapacitationDueToMovements());
        surveyData.put("patientAwareness", survey.getPatientAwareness());
        surveyData.put("emotionalDistress", survey.getEmotionalDistress());
        surveyData.put("globalRating", survey.getGlobalRating());

        // 🔹 Get ML prediction (severity + assessment + suggestions)
        @SuppressWarnings("unchecked")
        Map<String, Object> result = mlService.getPredictionRaw((Map<String, Object>) (Map<?, ?>) surveyData);

        String severityScore = String.valueOf(result.getOrDefault("severityScore", "N/A"));
        String assessment = String.valueOf(result.getOrDefault("assessment", "Unavailable"));
        Object suggestionsObj = result.get("suggestions");

        // 🔹 Handle suggestions (list or string)
        String suggestionsText = "No recommendations.";
        if (suggestionsObj instanceof List) {
            @SuppressWarnings("unchecked")
            List<String> suggestionsList = (List<String>) suggestionsObj;
            suggestionsText = String.join("\n- ", suggestionsList);
            suggestionsText = "- " + suggestionsText; // make it a bullet list
        } else if (suggestionsObj != null) {
            suggestionsText = suggestionsObj.toString();
        }

        // 🔹 Add values to PDF
        addLabelValue(document, "Predicted Severity Score", severityScore, labelFont, valueFont);
        addLabelValue(document, "Assessment", assessment, labelFont, valueFont);

        document.add(new Paragraph("Recommendations:", labelFont));
        document.add(new Paragraph(suggestionsText, valueFont));
        document.add(Chunk.NEWLINE);
    }

    private void addChartImage(Document document, String base64) {
        if (base64 == null || !base64.startsWith("data:image")) return;

        try {
            byte[] imageBytes = Base64.getDecoder().decode(base64.split(",")[1]);
            Image chartImage = Image.getInstance(imageBytes);
            chartImage.scaleToFit(500, 300);
            chartImage.setAlignment(Element.ALIGN_CENTER);

            document.add(new Paragraph("Survey Chart", sectionFont()));
            document.add(Chunk.NEWLINE);
            document.add(chartImage);
            document.add(Chunk.NEWLINE);
        } catch (Exception e) {
            System.err.println("Chart image could not be loaded: " + e.getMessage());
        }
    }

    private void addLabelValue(Document document, String label, String value, Font labelFont, Font valueFont) throws DocumentException {
        Paragraph p = new Paragraph();
        p.add(new Chunk(label + ": ", labelFont));
        p.add(new Chunk(value, valueFont));
        p.setSpacingAfter(5);
        document.add(p);
    }

    private void addTableHeader(PdfPTable table, String headerText, Font font) {
        PdfPCell cell = new PdfPCell(new Phrase(headerText, font));
        cell.setBackgroundColor(BaseColor.LIGHT_GRAY);
        cell.setHorizontalAlignment(Element.ALIGN_CENTER);
        cell.setPadding(8);
        table.addCell(cell);
    }

    private boolean addStyledRow(PdfPTable table, String label, int value, Font font, boolean shaded) {
        BaseColor bgColor = shaded ? new BaseColor(245, 245, 245) : BaseColor.WHITE;

        PdfPCell labelCell = new PdfPCell(new Phrase(label, font));
        labelCell.setBackgroundColor(bgColor);
        labelCell.setPadding(6);

        PdfPCell valueCell = new PdfPCell(new Phrase(String.valueOf(value), font));
        valueCell.setBackgroundColor(bgColor);
        valueCell.setHorizontalAlignment(Element.ALIGN_CENTER);
        valueCell.setPadding(6);

        table.addCell(labelCell);
        table.addCell(valueCell);

        return !shaded;
    }

    private void addOtherIssuesSection(Document document, Survey survey) throws DocumentException {
        if (survey.getOtherIssues() != null && !survey.getOtherIssues().trim().isEmpty()) {
            Font boldFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12);
            Font normalFont = FontFactory.getFont(FontFactory.HELVETICA, 12);

            Paragraph para = new Paragraph();
            para.setSpacingBefore(10f);
            para.setSpacingAfter(10f);

            Chunk label = new Chunk("Other Reported Issues: ", boldFont);
            Chunk value = new Chunk(survey.getOtherIssues().trim(), normalFont);

            para.add(label);
            para.add(value);

            document.add(para);
        }
    }

    // Shared fonts
    private Font sectionFont() {
        return new Font(Font.FontFamily.HELVETICA, 14, Font.BOLD, BaseColor.DARK_GRAY);
    }

    private Font boldFont() {
        return new Font(Font.FontFamily.HELVETICA, 12, Font.BOLD);
    }

    private Font normalFont() {
        return new Font(Font.FontFamily.HELVETICA, 12);
    }
}
