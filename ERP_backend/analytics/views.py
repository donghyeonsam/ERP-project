from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings


FALLBACK_MESSAGE = "AI 인사이트 기능을 사용하려면 .env 파일에 GMS_KEY(OpenAI API 키)를 설정해야 합니다."


@api_view(['POST'])
def demand_insight(request):
    """
    프론트에서 계산한 수요예측 통계치(요약)를 받아 OpenAI로 자연어 인사이트를 생성한다.
    실제 시계열 예측(숫자)은 프론트에서 통계적으로 계산하고, 여기서는 그 결과를
    해석하는 짧은 설명 문구만 생성한다 — 키가 없거나 호출이 실패해도 기능 전체가
    죽지 않도록 항상 200 + available 플래그로 응답한다.
    """
    if not settings.GMS_KEY:
        return Response({'available': False, 'insight': FALLBACK_MESSAGE})

    summary = request.data.get('summary', {})

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.GMS_KEY, base_url=settings.GMS_BASE_URL)

        prompt = (
            "다음은 식품 제조 ERP 시스템의 매출 수요예측 통계 요약이다. "
            "이 데이터를 근거로 경영진을 위한 짧은 인사이트(한국어, 3~4문장, 과장 없이 사실 기반)를 작성하라.\n\n"
            f"통계 요약: {summary}"
        )

        completion = client.chat.completions.create(
            model=settings.GMS_MODEL,
            messages=[
                {"role": "developer", "content": "너는 ERP 시스템의 수요예측 데이터를 해석해주는 데이터 분석가다."},
                {"role": "user", "content": prompt},
            ],
        )
        text = completion.choices[0].message.content.strip()
        return Response({'available': True, 'insight': text})
    except Exception as e:
        return Response({'available': False, 'insight': f'AI 인사이트 생성에 실패했습니다. ({e})'})
