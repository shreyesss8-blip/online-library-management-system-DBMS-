const fs = require("node:fs");
const path = require("node:path");

const { chromium } = require("C:/Users/SHREYES/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.59.1/node_modules/playwright");

const outDir = path.join(__dirname, "docs", "screenshots");
const base = "http://127.0.0.1:5000";

async function screenshot(page, name) {
    await page.screenshot({ path: path.join(outDir, name), fullPage: true });
}

async function run() {
    fs.mkdirSync(outDir, { recursive: true });

    const browser = await chromium.launch({
        headless: true,
        executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1024 } });

    await page.goto(base, { waitUntil: "networkidle" });
    await screenshot(page, "01-login-page.png");

    await page.fill('input[name="username"]', "admin");
    await page.fill('input[name="password"]', "wrong");
    await page.click('button[type="submit"]');
    await page.waitForLoadState("networkidle");

    await page.fill('input[name="username"]', "admin");
    await page.fill('input[name="password"]', "admin123");
    await page.click('button[type="submit"]');
    await page.waitForURL("**/dashboard");
    await page.waitForLoadState("networkidle");
    await screenshot(page, "02-dashboard.png");

    await page.goto(base + "/students", { waitUntil: "networkidle" });
    await page.fill('input[name="usn"]', "1VT22CS099");
    await page.fill('input[name="student_name"]', "Kiran Test");
    await page.selectOption('select[name="gender"]', "Male");
    await page.fill('input[name="department"]', "CSE");
    await page.fill('input[name="semester"]', "4");
    await page.fill('input[name="email"]', "kirantest99@vtu.edu");
    await page.fill('input[name="phone"]', "9876500999");
    await page.fill('input[name="join_date"]', "2026-05-16");
    await page.selectOption('select[name="status"]', "ACTIVE");
    await page.getByRole("button", { name: "Add Student" }).click();
    await page.waitForLoadState("networkidle");

    await page.goto(base + "/students/edit/11", { waitUntil: "networkidle" });
    await page.fill('input[name="student_name"]', "Kiran Kumar Test");
    await page.getByRole("button", { name: "Update Student" }).click();
    await page.waitForLoadState("networkidle");

    await page.goto(base + "/books/add", { waitUntil: "networkidle" });
    await screenshot(page, "03-add-book-page.png");
    await page.fill('input[name="title"]', "Flask DBMS Practical Guide");
    await page.fill('input[name="isbn"]', "9781234567899");
    await page.selectOption('select[name="author_id"]', { index: 1 });
    await page.selectOption('select[name="category_id"]', { index: 1 });
    await page.fill('input[name="publisher"]', "Campus Learning");
    await page.fill('input[name="published_year"]', "2024");
    await page.fill('input[name="total_copies"]', "3");
    await page.fill('input[name="shelf_no"]', "R1-S9");
    await page.fill('textarea[name="description"]', "Reference book used for DBMS mini project demonstration.");
    await page.getByRole("button", { name: "Save Book" }).click();
    await page.waitForURL("**/books");
    await page.waitForLoadState("networkidle");

    await page.fill('input[name="search"]', "Flask DBMS");
    await page.getByRole("button", { name: "Search" }).click();
    await page.waitForLoadState("networkidle");
    await screenshot(page, "04-search-books-page.png");
    await page.getByRole("link", { name: "Edit" }).click();
    await page.waitForLoadState("networkidle");
    await page.fill('input[name="publisher"]', "Campus Learning House");
    await page.getByRole("button", { name: "Update Book" }).click();
    await page.waitForURL("**/books");
    await page.waitForLoadState("networkidle");

    await page.goto(base + "/issue", { waitUntil: "networkidle" });
    await screenshot(page, "05-issue-book-page.png");
    await page.selectOption('select[name="student_id"]', "11");
    const options = await page.locator('select[name="book_id"] option').evaluateAll((nodes) =>
        nodes.map((node) => ({ value: node.value, text: node.textContent }))
    );
    const target = options.find((option) => option.text && option.text.includes("Flask DBMS Practical Guide"));
    await page.selectOption('select[name="book_id"]', target.value);
    await page.fill('input[name="issue_date"]', "2026-05-16");
    await page.fill('input[name="due_date"]', "2026-05-26");
    await page.getByRole("button", { name: "Issue Book" }).click();
    await page.waitForURL("**/history");
    await page.waitForLoadState("networkidle");

    await page.goto(base + "/return", { waitUntil: "networkidle" });
    await screenshot(page, "06-return-book-page.png");
    const borrowId = (await page.locator("tbody tr", { hasText: "Kiran Kumar Test" }).locator("td").nth(0).textContent()).trim();
    await page.fill('input[name="borrow_id"]', borrowId);
    await page.fill('input[name="return_date"]', "2026-05-29");
    await page.getByRole("button", { name: "Return Book" }).click();
    await page.waitForURL("**/history");
    await page.waitForLoadState("networkidle");

    await page.goto(base + "/reports", { waitUntil: "networkidle" });
    await screenshot(page, "07-reports-page.png");

    await page.goto(base + "/dashboard", { waitUntil: "networkidle" });
    await screenshot(page, "08-dashboard-stats.png");

    await page.goto("file:///C:/Users/SHREYES/Documents/Codex/2026-05-16/online-library-management-system/docs/sql-output.html", {
        waitUntil: "load",
    });
    await screenshot(page, "09-sql-output.png");

    await browser.close();
    console.log(`Screenshots saved to ${outDir}`);
}

run().catch((error) => {
    console.error(error);
    process.exit(1);
});
