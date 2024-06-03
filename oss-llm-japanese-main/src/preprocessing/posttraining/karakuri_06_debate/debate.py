import os, datetime, time, json
import pandas as pd
import torch
from datetime import timezone, timedelta
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer
from datasets import load_dataset
import random

model = AutoAWQForCausalLM.from_quantized(
    "GENIAC-Team-Ozaki/karakuri-lm-8x7b-chat-v0.1-awq",
    fuse_layers=True,
    trust_remote_code=False,
    safetensors=True,
)

tokenizer = AutoTokenizer.from_pretrained(
    "GENIAC-Team-Ozaki/karakuri-lm-8x7b-chat-v0.1-awq",
    trust_remote_code=False,
)

json_file_path = os.path.join('/home/user', 'dibate_select.jsonl')
skip_file_path = os.path.join('/home/user', 'dibate_select_skip.txt')

instruction_1=[
"以下の議題に対する肯定立論はどんなものになるか説明してください．",
"以下の議題について，肯定の立論を作成してください．",
"以下の議題について，肯定の立場からの主張を考えてください．",
"以下の議題について，肯定する主張を提案してください．",
"以下の議題に対して肯定する立場から立論してください．"
]

instruction_2=[
"以下の議題に対して否定する立場から立論してください．",
"以下の議題に対する否定立論はどんなものになるか説明してください．",
"以下の議題について，否定の立場からの主張を考えてください．",
"以下の議題について，否定の立論を作成してください．",
"以下の議題について，否定する主張を提案してください．"
]

def generate_response(model, tokenizer, input_ids, attention_mask, max_new_tokens):
    start_time = time.time()
    # outputs = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.99, top_p=0.95)
    outputs = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7, top_p=0.8)
    end_time = time.time()
    elapsed_time = end_time - start_time
    generated_text = tokenizer.decode(outputs[0][input_ids.shape[-1]:])
    return generated_text, elapsed_time



def send_prompt(prompt, topic, task):
    # print(prompt)
    eos = False
    generated_text = ''
    try:
        if len(prompt)<=2000:
            messages = [{"role": "user", "content": prompt}]
            input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt").cuda()
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            attention_mask = input_ids.ne(tokenizer.pad_token_id).int()
            generated_text, elapsed_time = generate_response(model, tokenizer, input_ids, attention_mask, 1024)
            if '</s>' not in generated_text:
                generated_text, elapsed_time = generate_response(model, tokenizer, input_ids, attention_mask, 512*4)
            if '</s>' in generated_text:
                eos = True
            generated_text = generated_text.replace('</s>', '')
            if task == 1:
                data_instruction = random.choice(instruction_1)
            else:
                data_instruction = random.choice(instruction_2)
            data = {
                "instruction": data_instruction,
                "input": topic,
                "output": generated_text,
                "prompt": prompt,
                "eos": eos,
                'time': f"{elapsed_time:.2f}"
            }
            with open(json_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Error at {prompt}: {e}")
        with open(skip_file_path, 'a', encoding='utf-8') as skip_file:
            skip_file.write(f"{prompt}\n")
        # continue  # 例外が発生した場合はこのインデックスをスキップ




shingidai = ['学校は部活動をさらに増やすべきである',
 '宇宙探査は人類の未来に必要である',
 '日本は海洋プラスチックごみ対策を強化すべきである',
 '国際連合は世界平和の維持に効果的である',
 '日本は遺伝子組み換え食品の販売を禁止すべきである',
 '恋愛において意見の違いを建設的に解決するべきである',
 '日本は全ての小中学校にエアコンを設置すべきである',
 '日本はサマータイム制を導入すべきである',
 '日本は鉄道の運賃を自由化するべきである',
 '学校は読書の時間を増やすべきである',
 '日本はペットの飼育規制を厳格化するべきである',
 '人間の意識は脳の活動である',
 '幸せを感じるために趣味に時間を使うべきである',
 '日本は公共交通機関の運賃を無料にするべきである',
 '道徳は普遍的である',
 '日本は森林保護を強化すべきである',
 '子どもはお友達と仲良くすべきである',
 '子どもは自転車に乗る練習をするべきである',
 '日本は消費税率を上げるべきである',
 'デート費用は男女平等に分担するべきである',
 '日本は環境税を導入すべきである',
 '日々の生活に運動を取り入れるべきである',
 '気候変動は国際協力によって解決できる',
 '日本は首都機能を東京から移転すべきである',
 '日本のごみ収集は全て有料化すべきである',
 '動物実験は倫理的に許されるべきである',
 '日本は公立学校における給食費を無料化するべきである',
 '日本は大学の学費を無料にするべきである',
 '子どもは毎日一時間は外で遊ぶべきである',
 '友達と遊ぶ時間をたくさん作るべきである',
 '日本は観光産業を振興すべきである',
 '恋愛関係においてプライバシーの尊重は重要である',
 '感情は正直に伝えるべきである',
 'クローン技術は積極的に発展させるべきである',
 '子どもはお小遣いを貯金するべきである',
 '日本はすべての原子力発電を代替発電に切り替えるべきである',
 '幸せを感じるために、自然と触れ合う機会を増やすべきである',
 '国は自国の文化を保護するべきである',
 '拡張現実は私たちの生活を豊かにする',
 '自分の時間を持つことは、幸せのために重要である',
 '人工知能は人間の仕事を奪う脅威となるべきである',
 '死刑制度は許されるべきである',
 '遺伝子編集技術は人間の進化に貢献するべきである',
 '日本はすべての動物園を廃止すべきである',
 '日本は高速道路を全面無料化するべきである',
 '学校は恋愛に関する教育を充実させるべきである',
 '生命の価値は何によって決まるべきである',
 '日本は防衛費を増額すべきである',
 '学校はプールの時間を増やすべきである',
 'カップルはお互いのSNSアカウントを共有するべきである',
 '芸術は社会にとって必要であるべきである',
 '日本は介護職の待遇を改善すべきである',
 '日本は積極的安楽死を法的に認めるべきである',
 '学校は給食をおいしくするべきである',
 '日本は災害対策を強化すべきである',
 '日本は選挙の棄権に罰則を設けるべきである',
 '国際的な紛争解決において軍事介入は正当化されるべきである',
 '日本はTPPに参加すべきである',
 '日本は地方創生のために都市部から地方への移住を奨励すべきである',
 '日本は義務教育において英語教育を強化すべきである',
 '日本は最低賃金を大幅に引き上げるべきである',
 '日本は再生可能エネルギーへの投資を増加すべきである',
 '日々のストレスを管理する方法を学ぶべきである',
 '日本は死刑制度を廃止すべきである',
 '学校は音楽の時間を増やすべきである',
 '子どもは早寝早起きをするべきである',
 '学校は図工の時間を増やすべきである',
 '幸福とは何かを定義するべきである',
 '人はポジティブな自己認識を育むべきである',
 '日本は食品ロスを削減するための法律を制定すべきである',
 '日本はプラスチック製品の使用を全面禁止すべきである',
 'グローバリゼーションは世界経済の成長を促進するべきである',
 'サイバーセキュリティは国家安全保障上の最優先事項であるべきである',
 '学校はもっと楽しいイベントを開催すべきである',
 '社会はメンタルヘルスのケアを重視するべきである',
 '移民は受け入れ国の経済に貢献するべきである',
 '臓器移植は倫理的に許されるべきである',
 '恋愛関係において、過去の恋愛を話し合うべきである',
 'みんなでゴミを拾う活動をするべきである',
 '恋愛において、互いの成長をサポートするべきである',
 '学校は給食にもっと野菜を出すべきである',
 '国際援助は貧困国の発展に効果的であるべきである',
 '日本は司法取引制度を導入すべきである',
 '子どもは本をたくさん読むべきである',
 '家庭でペットを飼うべきである',
 'カップルは定期的にお互いの期待を確認するべきである',
 '学校は科学実験の授業を増やすべきである',
 '各国は核兵器を廃絶するべきである',
 '恋人同士は記念日を大切にするべきである',
 'カップルはお互いに感謝の気持ちを表現するべきである',
 '幸せを感じるために、睡眠をしっかりとるべきである',
 '学校は楽しい授業をもっと増やすべきである',
 '人は日々感謝の気持ちを表現するべきである',
 '日本は食品の安全基準を厳格化するべきである',
 '子どもは自分の部屋をきれいにすべきである',
 '子どもは家でお手伝いをするべきである',
 '幸せを追求するために、夢や目標を持つべきである',
 '日本は週休3日制を導入すべきである',
 '日本は未成年者の携帯電話使用を大幅に制限すべきである',
 '自動運転車は交通事故を減らすべきである',
 '日本は障がい者の雇用機会を拡大すべきである',
 '安楽死は合法化されるべきである',
 '日本は教育現場でのいじめ対策を強化すべきである',
 '日本はインターネットの規制を強化すべきである',
 '学校はもっと楽しい遠足を計画すべきである',
 '学校は夏休みをもっと長くすべきである',
 '学校にいじめが存在するのはしょうがないことである',
 '誕生日はお祝いをするべきである',
 '日本は女性の社会進出を促進すべきである',
 '日本の救急車の利用は有料化すべきである',
 'バイオテクノロジーは食糧問題の解決に貢献する',
 '地方自治体は中学生以上による住民投票制度を制定すべきである',
 '日本は大統領制を導入すべきである',
 '職場の人間関係を重視すべきである',
 '日本は電気自動車の普及を推進すべきである',
 '先生は体罰を使うべきである',
 '日本は中学生以下のスマートフォンなどの使用を禁止すべきである',
 '日本はタクシーに関する規制を緩和すべきである',
 '核エネルギーは持続可能なエネルギー源となりうる',
 '日本は子育て支援を拡充すべきである',
 '人工知能は意識を持つことができるべきである',
 '日本は外国人労働者の受け入れを拡大すべきである',
 '先生は生徒には優しく接するべきである',
 '日本は農業支援を強化すべきである',
 '日本は飲食店での全面禁煙を義務付けるべきである',
 '日本は中学校高等学校の部活動制度を廃止すべきである',
 'カップルはお互いの友人関係を尊重するべきである',
 '学校は毎日掃除の時間を設けるべきである',
 '日本は中小企業支援を強化すべきである',
 '日本は学校の制服を廃止すべきである',
 '日本は地方自治体への財政支援を増加すべきである',
 '家族や友人との時間を大切にするべきである',
 '遠距離恋愛カップルは月に一度は会うべきである',
 '日本はレジ袋税を導入すべきである',
 '宿題は少なくすべきである',
 'カップルは趣味を共有するべきである',
]


# データセットのロード
dataset = load_dataset("GENIAC-Team-Ozaki/debate_argument_qa_dataset_ja", split="train")

# データフレームに変換
df = pd.DataFrame(dataset)

# 指定されたinstructionのリスト
specified_instructions = [
    "以下の議題に対する肯定立論はどんなものになるか説明してください．",
    "以下の議題について，肯定の立論を作成してください．",
    "以下の議題について，肯定の立場からの主張を考えてください．",
    "以下の議題について，肯定する主張を提案してください．",
    "以下の議題に対して肯定する立場から立論してください．"
]

# 指定されたinstructionのデータフレーム
df_specified = df[df['instruction'].isin(specified_instructions)]

# その他のデータフレーム
df_other = df[~df['instruction'].isin(specified_instructions)]


def generate_response(model, tokenizer, input_ids, attention_mask, max_new_tokens):
    start_time = time.time()
    outputs = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.99, top_p=0.95)
    # outputs = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7, top_p=0.8)
    end_time = time.time()
    elapsed_time = end_time - start_time
    generated_text = tokenizer.decode(outputs[0][input_ids.shape[-1]:])
    return generated_text, elapsed_time


# for i in range(2):
#     if i==0:
#         for topic in shingidai:
#             # 重複なしでランダムに3件を抽出
#             df_random_sample = df_specified.drop_duplicates().sample(n=2)
#             prompt = f"""議題に対する肯定立論を作成します。2つは例です。3つ目の議題に対する肯定立論を作成してください。

# 議題：{df_random_sample.iloc[0]['input']}
# 肯定立論：
# {df_random_sample.iloc[0]['output']}

# 議題：{df_random_sample.iloc[1]['input']}
# 肯定立論：
# {df_random_sample.iloc[1]['output']}

# 議題：{topic}
# 肯定立論：
# """
#             send_prompt(prompt, topic, 1)
#     else:
#         for topic in shingidai:
#             # 重複なしでランダムに3件を抽出
#             df_random_sample = df_other.drop_duplicates().sample(n=2)
#             prompt = f"""議題に対する否定立論を作成します。2つは例です。3つ目の議題に対する否定立論を作成してください。

# 議題：{df_random_sample.iloc[0]['input']}
# 否定立論：
# {df_random_sample.iloc[0]['output']}

# 議題：{df_random_sample.iloc[1]['input']}
# 否定立論：
# {df_random_sample.iloc[1]['output']}

# 議題：{topic}
# 否定立論：
# """
#             send_prompt(prompt, topic, 2)



# for i in range(2):
#     if i==0:
#         for topic in shingidai:
#             prompt = f"""議題に対する肯定立論を作成します。3つは例です。4つ目の議題に対する肯定立論を作成してください。

# 議題：日本はすべての石炭火力発電を代替発電に切り替えるべきである
# 肯定立論：
# 国立環境研究所の調査では、日本の再エネ導入ポテンシャルは、年間発電電力量として7万3000億kWh、そのうち経済性を考慮した導入可能量は2万6000億kWhと見積もられています。石炭火力は、SO2やNOXを発し、日本で稼働中の石炭火力発電所は、毎年1117人の早期死亡者を出し、新規の発電所ができれば、さらに年間455人の早期死亡者が増えると推計されています。石炭の価格は国際情勢によって変動します。再エネは国際情勢に関係しないため、価格変動のリスクは極めて低く、安定しています。送電線の増強、大型蓄電池、または揚水発電の導入を必要な箇所で行います。

# 議題：日本は中学校高等学校の部活動制度を廃止すべきである
# 肯定立論：
# 中学校・高等学校の部活動制度は、教員の過重労働や未経験分野での指導強制といった問題を引き起こし、教員の疲弊や精神疾患リスクを高めている。部活動は実績が重視されるため際限なく加熱しやすく、時間割で管理された授業とは異なり、際限のない時間外労働を招く。その結果、教員の帰宅時間は20時以降となり、土日も活動がある場合は、過労死ラインの月80時間を超える残業を強いられる。さらに、87.5%の中学校で教員全員に部活動指導が強制されており、半数近くの教員が未経験分野を担当している。この状況は、教員に過度な負担と精神的苦痛を与え、精神疾患の増加にもつながっている。これらのことから、教員の負担軽減、健康を守るため、部活動制度は廃止すべきである。

# 議題：日本の首都機能は東京から大阪に移転させるべきである
# 肯定立論：
# 日本の首都機能を大阪に移転することは、政治・経済の両面で東京一極集中を是正し、国のリスク分散に繋がると考えます。日本は地震や台風などの自然災害が多く、政治経済の中枢機能が東京に集中している現状は、大規模災害発生時の国家運営に深刻な支障をきたす恐れがあります。首都機能を大阪に移転することで、災害時の代替機能を確保し、国家のレジリエンスを高めることが可能です。また、大阪は既に経済基盤が確立されており、交通インフラも整備されているため、首都機能移転に適した環境が整っています。これらのことから、首都機能の大阪移転は、日本の防災対策および危機管理体制の強化に不可欠な施策であると言えます。

# 議題：{topic}
# 肯定立論：
# """
#             send_prompt(prompt, topic, 1)
#     else:
#         for topic in shingidai:
#             prompt = f"""議題に対する否定立論を作成します。2つは例です。3つ目の議題に対する否定立論を「200文字以内で」作成してください。

# 議題：日本は富裕層に対する資産課税を強化すべきである
# 否定立論：
# 富裕層への課税強化は、経済活動の停滞、資本流出のリスク、複雑な制度運営、不公平感の増大といった問題を引き起こす可能性があります。富裕層は消費や投資の大部分を担っているため、彼らの活動が縮小すると経済成長が停滞する恐れがあります。また、過度な課税は資本の海外流出を招き、国内の投資が減少し経済に悪影響を及ぼす可能性もあります。資産課税の強化には複雑な税制運営が必要となり、行政コストが増大します。資産の評価方法や税率の設定など、具体的な運用には多くの課題があり、不適切な運用が行われると税収確保が困難になる可能性もあります。さらに、富裕層への課税強化は公平性の観点からも問題があります。富裕層が特定の負担を強いられることで、彼らの間に不満が生じ、社会的な分断を招く恐れがあります。特に、企業オーナーや経営者層の反発が強まることで、ビジネス環境が悪化するリスクもあります。

# 議題：日本はすべての石炭火力発電を代替発電に切り替えるべきである
# 否定立論：
# エネルギー安全保障は国民の生命と財産を守る上で最優先事項であり、エネルギー資源のほぼ全てを海外からの供給に依存する日本にとって、安定供給と経済性に優れた石炭火力発電は重要な役割を担っています。石炭は他の化石燃料と比べて供給が安定しており、価格も低いため、LNG火力発電よりも低いコストで発電できます。さらに、IEAの予測では石炭価格は将来的に下がる見込みです。電力供給において需要と供給のバランスは重要であり、太陽光発電などの再生可能エネルギーは天候によって不安定なため、安定的な火力発電が必要となります。再生可能エネルギーの大量導入は電力網の増強費用を膨らませ、電気料金の上昇を招きます。また、太陽光発電の導入拡大は停電リスクも高めます。停電は病院などにおいて深刻な影響を及ぼす可能性があり、エネルギー安全保障の観点から石炭火力発電の廃止は再考すべきです。

# 議題：学校は飲み物の自動販売機を設置すべきである
# 否定立論：
# 学校への清涼飲料水自動販売機の設置は、生徒の健康、学習環境、経済状況への悪影響を考慮すると、適切ではないと考えます。まず自動販売機で販売される清涼飲料水には、糖分やカフェインが多く含まれており、生徒の過剰摂取が懸念されます。これらの成分は、短期的には疲労回復効果があるかもしれませんが、長期的な健康への悪影響が懸念されます。特に成長期の生徒にとっては、糖分の過剰摂取は肥満や虫歯のリスクを高める可能性があります。次に自動販売機の設置は、学習環境の悪化を招く可能性があります。生徒が授業中や休憩時間に自動販売機を利用するために移動する頻度が増えれば、授業への集中力低下や授業進行の妨げになる可能性があります。また、自動販売機周辺に生徒が集まることで、騒音や混雑が発生し、他の生徒の学習環境を阻害する可能性も否定できません。以上の理由から、学校への清涼飲料水自動販売機の設置は、生徒の健康、学習環境、経済状況への悪影響を考慮すると、再考すべき提案であると結論付けます。

# 議題：{topic}
# 否定立論：
# """
#             send_prompt(prompt, topic, 2)


# for i in range(1):
#     if i==0:
#         for topic in shingidai:
#             prompt = f"""議題に対する論拠を作成します。3つは例です。4つ目の議題に対する論拠を一つだけ作成してください。

# 議題：日本は富裕層に対する資産課税を強化すべきではない
# 論拠：
# 富裕層への課税強化は、経済活動の停滞、資本流出のリスク、複雑な制度運営、不公平感の増大といった問題を引き起こす可能性があります。富裕層は消費や投資の大部分を担っているため、彼らの活動が縮小すると経済成長が停滞する恐れがあります。また、過度な課税は資本の海外流出を招き、国内の投資が減少し経済に悪影響を及ぼす可能性もあります。資産課税の強化には複雑な税制運営が必要となり、行政コストが増大します。資産の評価方法や税率の設定など、具体的な運用には多くの課題があり、不適切な運用が行われると税収確保が困難になる可能性もあります。さらに、富裕層への課税強化は公平性の観点からも問題があります。富裕層が特定の負担を強いられることで、彼らの間に不満が生じ、社会的な分断を招く恐れがあります。特に、企業オーナーや経営者層の反発が強まることで、ビジネス環境が悪化するリスクもあります。

# 議題：日本はすべての石炭火力発電を代替発電に切り替えるべきではない
# 論拠：
# エネルギー安全保障は国民の生命と財産を守る上で最優先事項であり、エネルギー資源のほぼ全てを海外からの供給に依存する日本にとって、安定供給と経済性に優れた石炭火力発電は重要な役割を担っています。石炭は他の化石燃料と比べて供給が安定しており、価格も低いため、LNG火力発電よりも低いコストで発電できます。さらに、IEAの予測では石炭価格は将来的に下がる見込みです。電力供給において需要と供給のバランスは重要であり、太陽光発電などの再生可能エネルギーは天候によって不安定なため、安定的な火力発電が必要となります。再生可能エネルギーの大量導入は電力網の増強費用を膨らませ、電気料金の上昇を招きます。また、太陽光発電の導入拡大は停電リスクも高めます。停電は病院などにおいて深刻な影響を及ぼす可能性があり、エネルギー安全保障の観点から石炭火力発電の廃止は再考すべきです。

# 議題：学校は飲み物の自動販売機を設置すべきではない
# 論拠：
# 学校への清涼飲料水自動販売機の設置は、生徒の健康、学習環境、経済状況への悪影響を考慮すると、適切ではないと考えます。まず自動販売機で販売される清涼飲料水には、糖分やカフェインが多く含まれており、生徒の過剰摂取が懸念されます。これらの成分は、短期的には疲労回復効果があるかもしれませんが、長期的な健康への悪影響が懸念されます。特に成長期の生徒にとっては、糖分の過剰摂取は肥満や虫歯のリスクを高める可能性があります。次に自動販売機の設置は、学習環境の悪化を招く可能性があります。生徒が授業中や休憩時間に自動販売機を利用するために移動する頻度が増えれば、授業への集中力低下や授業進行の妨げになる可能性があります。また、自動販売機周辺に生徒が集まることで、騒音や混雑が発生し、他の生徒の学習環境を阻害する可能性も否定できません。以上の理由から、学校への清涼飲料水自動販売機の設置は、生徒の健康、学習環境、経済状況への悪影響を考慮すると、再考すべき提案であると結論付けます。

# 議題：{topic}
# 論拠：
# """
#             send_prompt(prompt, topic, 1)


for i in range(1):
    if i==0:
        for topic in shingidai:
            prompt = f"""以下の議題について、肯定の立場からの主張を作成してください。

### 例1
議題：日本はすべての石炭火力発電を代替発電に切り替えるべきである
肯定立論：国立環境研究所の調査では、日本の再エネ導入ポテンシャルは、年間発電電力量として7万3000億kWh、そのうち経済性を考慮した導入可能量は2万6000億kWhと見積もられています。石炭火力は、SO2やNOXを発し、日本で稼働中の石炭火力発電所は、毎年1117人の早期死亡者を出し、新規の発電所ができれば、さらに年間455人の早期死亡者が増えると推計されています。石炭の価格は国際情勢によって変動します。再エネは国際情勢に関係しないため、価格変動のリスクは極めて低く、安定しています。送電線の増強、大型蓄電池、または揚水発電の導入を必要な箇所で行います。

### 例2
議題：日本の首都機能は東京から大阪に移転させるべきである
肯定立論：日本の首都機能を大阪に移転することは、政治・経済の両面で東京一極集中を是正し、国のリスク分散に繋がると考えます。日本は地震や台風などの自然災害が多く、政治経済の中枢機能が東京に集中している現状は、大規模災害発生時の国家運営に深刻な支障をきたす恐れがあります。首都機能を大阪に移転することで、災害時の代替機能を確保し、国家のレジリエンスを高めることが可能です。また、大阪は既に経済基盤が確立されており、交通インフラも整備されているため、首都機能移転に適した環境が整っています。これらのことから、首都機能の大阪移転は、日本の防災対策および危機管理体制の強化に不可欠な施策であると言えます。

### 議題
{topic}

### 肯定立論
"""
            send_prompt(prompt, topic, 1)
