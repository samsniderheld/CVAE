using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This script is responsible for taking the camera output and rendering it to a png.
/// Users can define the output resoultion they like.Images are stored in a byte array during
/// runtime and saved at the end. This script is controlled by the RenderPointCloud script.
/// </summary>

public class RenderImages : MonoBehaviour
{
    //public variables
    [HideInInspector]
    public byte[][] allBytesArrays;

    public bool takePhotos = false;


    //private variables accessible in the editor
    [SerializeField]
    private int resolutionX = 240;

    [SerializeField]
    private int resolutionY = 135;

    [SerializeField]
    private RenderTexture renderTexture;


    //private variables not accessible in the editor
    private Camera camera;

    private Texture2D screenShot;

    private Texture2D newTexture;


    private string outputPath = "/Your/Output/Path/Here/";

    private int outputFrameIndex = 0;

    void Start()
    {
        camera = Camera.main;

        screenShot = new Texture2D(resolutionX, resolutionY, TextureFormat.RGB24, true);

        newTexture = new Texture2D(128, 128, TextureFormat.RGB24, true);

    }

    public void StoreImage(){

         if(renderTexture == null){
            return;
        }

        RenderTexture.active = renderTexture;
        newTexture.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        newTexture.Apply();

        var rt = RenderTexture.GetTemporary(resolutionX, resolutionY, 24);
        
        camera.targetTexture = rt;
		camera.Render();
		RenderTexture.active = rt;
		screenShot.ReadPixels(new Rect(0, 0, resolutionX, resolutionY), 0, 0, false);
		camera.targetTexture = null;
		RenderTexture.active = null; // JC: added to avoid errors

        RenderTexture.ReleaseTemporary(rt);

        allBytesArrays[outputFrameIndex] = screenShot.EncodeToPNG();

        outputFrameIndex+=1;


    }

    public void SaveAllImages(){

        camera.enabled = false;

        for(int i = 0; i<outputFrameIndex;i++){
            System.IO.File.WriteAllBytes(outputPath + "/" +  i.ToString("0000") + ".png", allBytesArrays[i]);
        }
    }

    
}
