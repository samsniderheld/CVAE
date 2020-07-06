using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This script is responsible for blitting the depth buffer to the camera output during runtime.
// via http://www.shaderslab.com/demo-50---grayscale-depending-zbuffer.html
/// </summary>

[ExecuteInEditMode]
public class DisplayDepth : MonoBehaviour
{
    [SerializeField]
    private Material mat;
 
    void Start()
    {
        GetComponent<Camera>().depthTextureMode = DepthTextureMode.Depth;
    }

    void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        Graphics.Blit(source, destination, mat);
    }
}
