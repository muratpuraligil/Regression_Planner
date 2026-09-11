# Jira - Dify Entegrasyon Rehberi & Skill Seti (JiraSkill)

Bu döküman, Jira Cloud ve Xray Cloud entegrasyonlarında tekrarlanan hataları (400, 410, Tırnak sorunları) engellemek için uyulması gereken zorunlu kuralları içerir.

## 1. JQL Arama (Search) Kuralları
- **Endpoint:** Artık `/rest/api/3/search` kullanılmamalıdır. Mutlaka **`/rest/api/3/search/jql`** uç noktası kullanılmalıdır.
- **İstek Formatı (Dify HTTP Node):** İstekler **POST** metoduyla yapılmalı ve JQL sorgusu `params` olarak DEĞİL, `BODY -> JSON` seçilerek gövdeden (raw text) gönderilmelidir:
  ```json
  {
    "jql": "project = YFMTEST AND issuetype = Test",
    "maxResults": 200,
    "fields": ["key", "summary", "parent"]
  }
  ```
- **Tırnak Kullanımı:** JQL içindeki tüm metin değerler (`project`, `fixVersion`, `status` vb.) mutlaka çift tırnak (`" "`) içinde olmalıdır.
- **Parametre Yapısı:** `fixVersion = "10.1.0"` yerine daha esnek olan `fixVersion in ("10.1.0")` yapısı tercih edilmelidir.
- **Dify Variables:** URL içinde kullanılan `{{#start.fixVersion#}}` gibi değişkenler URL encode edilirken `%7B%7B` şeklinde "bozulmamalı", YAML içinde saf haliyle kalmalıdır.

## 2. Issue Yaratma (Create Issue) Kuralları
- **Fix Version:** Bir issue yaratırken versiyon bilgisinin setlenmesi için sadece `summary` yeterli değildir. Aşağıdaki JSON yapısı `fields` içine eklenmelidir:
  ```json
  "fixVersions": [
    {
      "name": "{{#start.fixVersion#}}"
    }
  ]
  ```
- **Custom Fields:** `Is Regression` gibi seçim listeleri (dropdown) Jira'da nesne olarak tutulur:
  ```json
  "customfield_10184": {
    "value": "Yes"
  }
  ```

## 3. Xray GraphQL Entegrasyonu
- **Auth:** Xray authenticate API her zaman `POST` ile çağrılmalı ve alınan JWT token `Bearer` olarak kullanılmalıdır.
- **Linkleme:** Test Plan ve Execution bağlama işlemi `addTestExecutionsToTestPlan` mutation'ı ile yapılmalıdır.
- **Hata Yakalama:** Python kodunda her zaman API yanıtı `json.dumps(outputs, indent=2)` ile Dify `End` düğümüne raporlanmalıdır.

## 4. Dify HTTP Node Yapılandırması
- **Headers:** Header'lar her zaman boşluksuz ve temiz olmalıdır:
  ```text
  Authorization: Basic {{#env.jira_auth#}}
  Content-Type: application/json
  ```
- **Timeout:** Karmaşık JQL aramaları için `read timeout` değeri en az 60 saniye olmalıdır.

## 5. Kritik Hata Çözümleri (Troubleshooting)
- **"issueId provided is not valid" Hatası:** Xray GraphQL API, bazı mutasyonlarda Jira **Key** (Örn: ISCEPTEST-1) yerine Jira **Numeric ID** (Örn: 10001) bekler. Tüm linkleme işlemlerinde ID kullanılmalıdır.
- **Boş Liste Sorunu:** JQL sorgularında custom field değerleri (Dropdown) büyük/küçük harfe duyarlı olabilir. Sorguda `"YES"` yerine `"Yes"` (veya Jira'daki tam karşılığı) kullanılmalıdır.
- **Project Key vs Name:** Proje isimleri boşluk içeriyorsa hata verme riski yüksektir. JQL'de her zaman `project = ISCEPTEST` (Proje Anahtarı) kullanımı tercih edilmelidir.
