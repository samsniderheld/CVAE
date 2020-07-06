// Upgrade NOTE: replaced 'mul(UNITY_MATRIX_MVP,*)' with 'UnityObjectToClipPos(*)'

Shader "Custom/ZBuffer"
{
	Properties {

		_Start ("Start", Float) = 1
		_Front ("Front Modifier", Float) = 1
		_Back ("Back Modifier", Float) = -1
		_Mult ("Multiplier", Float) = 1

   	}

	SubShader
	{
		Tags { "RenderType"="Opaque" }

        Cull Off
        ZWrite Off 
        ZTest Always
		
		Pass
		{
			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#include "UnityCG.cginc"

			struct v2f
			{
				float4 pos : SV_POSITION;
				float4 screenuv : TEXCOORD1;
			};
			
			v2f vert (appdata_base v)
			{
				v2f o;
				o.pos = UnityObjectToClipPos(v.vertex);
				o.screenuv = ComputeScreenPos(o.pos);
				return o;
			}
			
			sampler2D _CameraDepthTexture;

			uniform float _Start;
			uniform float _Front;
			uniform float _Back;
			uniform float _Mult;

			float map(float value, float min1, float max1, float min2, float max2) {
				return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
			}

			fixed4 frag (v2f i) : SV_Target
			{
				float depth = SAMPLE_DEPTH_TEXTURE(_CameraDepthTexture,i.screenuv);
				float linearDepth = Linear01Depth(depth);
				float mappedDepth = map(linearDepth,0.0,1.0,_Front,_Back);
				
				return fixed4(mappedDepth, mappedDepth, mappedDepth, 1);
			}

			
			ENDCG
		}
	}
}