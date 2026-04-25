import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.File;
import java.io.FileInputStream;

public class ExcelReader {

    public static void main(String[] args) {

        try {
            String filePath = args[0];

            FileInputStream fis = new FileInputStream(new File(filePath));
            Workbook workbook = new XSSFWorkbook(fis);

            int total = 0;
            int pass = 0;
            int fail = 0;
            int blocked = 0;
            int notTest = 0;

            for (int s = 0; s < workbook.getNumberOfSheets(); s++) {

                Sheet sheet = workbook.getSheetAt(s);

                for (Row row : sheet) {

                    if (row == null || row.getRowNum() == 0) continue;

                    Cell cell = row.getCell(6, Row.MissingCellPolicy.CREATE_NULL_AS_BLANK);

                    String result = cell.toString().trim().toUpperCase();

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

            System.out.println("======================");
            System.out.println("TOTAL=" + total);
            System.out.println("PASS=" + pass);
            System.out.println("FAIL=" + fail);
            System.out.println("BLOCKED=" + blocked);
            System.out.println("NOT TEST=" + notTest);
            System.out.println("======================");

        } catch (Exception e) {
            e.printStackTrace();   // 🔥 이게 없으면 원인 안 보임
            System.exit(1);
        }
    }
}