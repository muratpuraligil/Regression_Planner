# YAFI Regresyon Planlayıcısı (YAFI Regression Planner) - Ürün Gereksinim Dokümanı (PRD)

Bu doküman, Dify.ai platformu üzerinde çalışan **YAFI Regression Planner** isimli iş akışının (workflow) amacını, arka plandaki çalışma mantığını ve süreci düğüm (node) bazında nasıl ilerlettiğini detaylandırmak için hazırlanmıştır.

## 1. Ürün Özeti

QA ekibinin koşturacağı regresyon testlerini Jira'dan otomatik oluşturan, Fonksiyonel test senaryolarını Epic/Parent bazlı kümülatif döngü ve rastgele karıştırma (random.shuffle) algoritması ile `RC {{fixVersion}} Functional-1..N` formatında "Test Execution" paketlerine bölen ve belirlenen 3 özel Non-Functional testi (`YFMTEST-3997`, `YFMTEST-4007`, `YFMTEST-4013`) `RC {{fixVersion}} Non-Functional-1..N` formatındaki paketlere aktaran bir otomasyon aracıdır. Tüm oluşturulan Test Execution paketleri otomatik olarak standart açıklama şablonuyla açılan ortak bir Test Planına (`RC Plan {{fixVersion}}`) bağlanır. Hem Dify sonuç ekranında hem de MS Teams bildirimlerinde tüm Test Plan ve Test Execution setleri **tıklanabilir doğrudan Jira linkleri (`https://commencis.atlassian.net/browse/{KEY}`)** olarak listelenir.

## 2. Girdi Parametreleri (Start Node Inputs)

1. **`FixVersion`** (`fixVersion`, Text): Required: `true`, Placeholder: `1.0.0`
2. **`Fonk.Koşum Set Sayısı`** (`exec_count`, Number): Required: `true`, Placeholder: `Set Sayısı`
3. **`Case Sayısı`** (`case_count`, Number): Required: `true`, Placeholder: `Case sayısı`
4. **`Non-Func.Koşum Set Sayısı`** (`non_func_exec_count`, Number): Required: `true`, Default: `2`

## 3. Tıklanabilir Doğrudan Linkler (Dify & Teams Entegrasyonu)

- **Dify Sonuç Ekranı:**
  Tüm `TestPlan` ve `Test Execution` paketleri Markdown formatında (`[İsim (KEY)](https://commencis.atlassian.net/browse/KEY)`) listelenir. Kullanıcılar tek tıkla ilgili Jira sayfasına gider.
- **MS Teams Bildirim Kartı (MessageCard):**
  Teams kanalına giden kartın metninde tüm linkler tıklanabilir köprü (hyperlink) olarak yer alır; ayrıca kartın altında doğrudan Test Planını açan **"🔗 {KEY} Test Planını Aç"** butonu bulunur.

## 4. Ortam Değişkenleri ve MS Teams Webhook Kurulumu

- **`jira_auth`** (String): Jira Basic Auth Token
- **`xray_client_id`** (String): Xray Client ID
- **`xray_client_secret`** (String): Xray Client Secret
- **`teamsWebhookUrl`** (String): MS Teams Webhook URL *(Opsiyonel)*

## 5. Dify İş Akışının Düğüm Düğüm (Node) Açıklaması

Sistem birbiri ardına tetiklenen 11 ana düğümden (Node) oluşmaktadır:

### 1. Start ➔ 2. Jira Fetch & 3. Jira Fetch Non-Func ➔ 4. Normalize Cases & 5. Distribute ➔ 6. Create Test Plan & 7. Parse Plan Key ➔ 8. Create Executions (ID ve Key'leri toplar) ➔ 9. Xray Linker (Linkli Markdown ve Teams payload oluşturur) ➔ 10. Teams URL Var mı? (If-Else) ➔ 11. End
