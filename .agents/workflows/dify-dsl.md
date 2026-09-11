---
description: Trigger the Dify DSL Architect skill to create a YAML workflow file.
---

Bu komut (workflow) çalıştırıldığında, yapay zeka asistanının doğrudan **Dify DSL Architect** yeteneğini (skill) devreye sokmasını sağlar.

## Steps

1. **Dify DSL Architect** yeteneğine ait olan ve `.agents/skills/dify_dsl_architect/SKILL.md` (veya taşınmışsa ilgili konumdaki) dosyasını okuyarak talimatları en ince ayrıntısına kadar özümse.
2. Kullanıcıya "Dify DSL Architect yeteneğim hazır! Lütfen oluşturmak istediğin iş akışını veya entegrasyon senaryosunu tarif et." şeklinde enerjik ve profesyonel bir karşılama yap.
3. Kullanıcının verdiği senaryoya göre SKILL.md dosyasındaki "Operational Protocol" ve "Technical Constraints" adımlarını *birebir* uygulayarak Dify uyumlu (v0.1.5 formatında) YAML dosyasını hazırla.
4. Dosyayı `output/` (veya kullanıcının belirttiği) klasör altına `.yml` formatında kaydet.
5. Kullanıcıya sonucu sunarken kapanış cümlesi olarak mutlaka şu ifadeyi kullan: **"Mimarinin iskeleti hazır Murat, bu dosyayı Dify'a yüklediğinde ruh bulacak. Test sırasında bir takılma olursa buradayım."**
