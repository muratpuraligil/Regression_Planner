# AI Regresyon Planlayıcısı (AI Regression Execution Planner) - Ürün Gereksinim Dokümanı (PRD)

Bu doküman, Dify.ai platformu üzerinde çalışan **AI Regression Execution Planner** isimli iş akışının (workflow) amacını, arka plandaki çalışma mantığını ve süreci düğüm (node) bazında nasıl ilerlettiğini detaylandırmak için hazırlanmıştır.

## 1. Ürün Özeti

QA ekibinin koşturacağı regresyon testlerini otomatik olarak getiren, mantıksal (Epic) bütünlüğünü bozmadan öncelik sırasına koyan ve sonrasında test yükünü 4 farklı "Test Execution" (Test Çalıştırma) paketine dağıtıp Xray/Jira üzerinde otomatik olarak oluşturan bir otomasyon aracıdır.

## 2. Testlerin Getirilme Şartları (Filtre / JQL)

İş akışı, test senaryolarını Jira'dan alırken iki farklı kaynaktan veri çeker:
1. **New Release JQL (Yeni Sürüm Filtresi):** `project="Iscep Test" and "Is Regression[Dropdown]" = YES and type = "Test" and fixVersion={{fixVersion}} ORDER BY parent ASC`
2. **Regresyon Filtresi (ID: 14716):** URL `https://commencis.atlassian.net/issues?filter=14716` adresinde önceden tanımlı donuk (sabit) regresyon test kaseleri kümesi.

Bu sayede sadece yeni sürüme özel spesifik regresyon kayıtları değil, her regreyonda koşması beklenen kemik senaryolar da havuza dahil edilir.

---

## 3. Test Caselerinin Dağıtım/Bölüştürülme Mantığı

İşlem, test yükünü %65 ve %35 sabit kurallı oranlarına bölmek üzerine tasarlanmış üç aşamalı, deterministik bir Python optimizasyon mimarisi üzerinde çalışır:

1. **Dağılım Hedefleri:** 4 ayrı "Test Execution" yaratılacaktır. Her bir Test Execution içerisine mutlak suretle **20 adet** test case alınacaktır:
   - **13 Şer Case (%65):** New Release JQL filtresinden.
   - **7 Şer Case (%35):** Regresyon Filtresinden.
   *(Toplam Havuz: Sistem 80 test case yaratır, 52 tanesi 1. Filtreden, 28 tanesi 2. Filtreden gelir).*

2. **Epic Bazlı Gruplama & Önceliklendirme:** Her iki filtreden gelen havuz öncelikle bağlı bulundukları **Epic (Parent)**'lara göre gruplanır. Ardından her epic içerisindeki caseler `Priority` (Öncelik) seviyesine göre **Highest -> High -> Medium -> Low -> Lowest** kurgusunda büyükten küçüğe dikey sıralanır.

3. **Atama Algoritması (Round-Robin):** Sistem 4 adet Test Execution kutusunu doldurmak üzere Epic'lerde gezmeye (döngü yapmaya) başlar:
   - Önce ilk Epic'ten listesinin en değerli (Highest) casini alır ve 1. Execution'a atar. 
   - Sonra hemen diğer Epic'e geçer ordakinin en iyi Case'ini alır ve 1. Execution'a atar. 
   - Eğer tüm Epicleri bir tur dönmesine rağmen hala (örneğin Release için) 13 kase hedefine ulaşılamadıysa, turu başa sarar ve aynı Epic'ten sıradaki (2. en iyi priority'li) kaseyi eklemeye devam eder.
   - 1. Execution için 13 Release + 7 Regresyon dolduğunda, 2. Execution için kaldığı yerden tur atlamaya devam eder. Bu işlem 4 execution da dolana kadar devam eder. (Regresyon filtresindeki karmaşık epic ağında yetersiz eşleşme olursa mevcut havuzdan rastgele yüksek priority seçme fallback kuralları da sisteme dahil edilmiştir).

---

## 4. Dify İş Akışının Düğüm Düğüm (Node) Açıklaması

Sistem birbiri ardına tetiklenen 7 ana düğümden (Node) oluşmaktadır:

### 1. Start (Başlangıç)
- **Tür:** Start Node
- **İşlev:** Kullanıcıdan `fixVersion` parametresini (`text-input`) girmesini bekler. Ayrıca, Xray GraphQL işlemleri için gerekli olan API anahtarları Dify'ın otomatik ortam değişkenlerinden okunur.

### 2. Jira Multi Fetch (Jira'dan Çiftli Veri Çekme)
- **Tür:** Code Node (Python 3)
- **İşlev:** Arka arkaya iki bağımsız HTTP GET isteği atılır:
  1. JQL 1: Girdiğiniz `fixVersion` sürüm numarasına sahip Release testleri.
  2. JQL 2: Sınırsız Regresyon (14716) filtresi.
- Python kodu her iki JSON dönütünü ayrıştırır ve içlerinden sadece `key`, `epic (parent/customfield_10008)`, `priority` bilgilerini süzüp veri kaynağı ile "Release" ve "Regression" etiketini basarak sonraki iterasyona paketler.

### 3. AI Epic Group (Analiz & Özet)
- **Tür:** LLM Node (OpenAI GPT-4o)
- **İşlev:** Verilerin genel tutarlılığını ve isimlendirmeleri analiz edip, JSON'ı daha insan-okunur (human-readable) bir özete kavuşturur. (Dağılım matematiğine müdahele etmesi veya test kipi atlaması engellenmiştir).

### 4. Distribute (Senaryo Dağıtımı ve Optimizasyon)
- **Tür:** Python Code Node
- **İşlev:** PRD'nin 3. Başlığında verilen %65/%35 (13+7) dağıtım kurallarını ve Epic (Highest -> Lowest) bazlı round-robin sıralama mantığını katı bir matematiksel doğruluyla yürütür. İşlem sonunda 4 ayrı paket olan `exec1_keys`, `exec2_keys`, `exec3_keys`, `exec4_keys` değerlerini virgülle ayrılmış text olarak dışa aktarır.

### 5. Create Test Plan & Parse Plan Key (Test Planının Açılması)
- **Tür:** HTTP Request Node ve Code Node (Python)
- **İşlev:** `Iscep Client RC {{fixVersion}}` isimli Test Plan Issue'su açılır ve ID'si parse edilir.

### 6. Create Exec 1, 2, 3, 4 (4 Adet Dağıtık Execution Yaratılması)
- **Tür:** HTTP Request Node (Çoklu - 4 Adet Paralel Node)
- **İşlev:** Toplam sistem dengelemesini sağlamak amacıyla, arayüzden gelen `execX_keys` havuzlarına ev sahipliği yapacak 4 ayrı `Iscep Client RC {{fixVersion}} - Execution 1..4` kaydı Issue olarak yaratılır. ( `Is Regression` parametreleri `Yes`'dir ).

### 7. Link in Xray Cloud (Tüm Verilerin Merge Edilmesi)
- **Tür:** Python Code Node (GraphQL)
- **İşlev:** 4 Test Execution kaydını ve 1 Ana Test Planını Xray üzerinden birbirine GraphQL (`addTestExecutionsToTestPlan`) ile linkler. Ve `Distribute` düğümünde hazırlanan 4 paketi ilgili Executionların içine (`addTestsToTestExecution`) enjekte ederek senaryoyu 0 efor kuralı ile sonlandırır.

### 8. End (Bitiş)
- **Tür:** End Node
- **İşlev:** Dify Loglama sunularak süreç onaylanır.
