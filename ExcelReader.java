import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.File;
import java.io.FileInputStream;

public class ExcelReader {

    public static void main(String[] args) {

        try {
            if (args.length < 1) {
                System.out.println("EXCEL FILE PATH REQUIRED");
                return;
            }

            String filePath = args[0];

            FileInputStream fis = new FileInputStream(new File(filePath));
            Workbook workbook = new XSSFWorkbook(fis);

            int total = 0;
            int pass = 0;
            int fail = 0;
            int blocked = 0;
            int notTest = 0;

            // =========================
            // 모든 Sheet 순회
            // =========================
            for (int s = 0; s < workbook.getNumberOfSheets(); s++) {

                Sheet sheet = workbook.getSheetAt(s);

                for (Row row : sheet) {

                    if (row.getRowNum() == 0) continue; // header skip

                    Cell resultCell = row.getCell(6); // result column (7번째)

                    if (resultCell == null) continue;

                    String result = resultCell.toString().trim().toUpperCase();

                    total++;

                    switch (result) {
                        case "PASS":
                            pass++;
                            break;
                        case "FAIL":
                            fail++;
                            break;
                        case "BLOCKED":
                            blocked++;
                            break;
                        default:
                            notTest++;
                            break;
                    }
                }
            }

            workbook.close();
            fis.close();

            // =========================
            // OUTPUT (Jenkins에서 읽기)
            // =========================
            System.out.println("======================");
            System.out.println("TOTAL   = " + total);
            System.out.println("PASS    = " + pass);
            System.out.println("FAIL    = " + fail);
            System.out.println("BLOCKED = " + blocked);
            System.out.println("NOT TEST= " + notTest);
            System.out.println("======================");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}