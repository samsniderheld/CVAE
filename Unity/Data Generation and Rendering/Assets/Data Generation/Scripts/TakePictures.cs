using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

/// <summary>
/// This script is responsible for generating all the unprocessed data for
/// the neural network. It essentially defines some basic parameters for
/// generating the number and size of the images you want.
/// </summary>

public class TakePictures : MonoBehaviour {

	[SerializeField]
	private bool canTakePictures = true;

	[SerializeField]
	private int numPics;

	[SerializeField]
	private int resWidth = 100; 

	[SerializeField]
	private int resHeight = 100;

	[SerializeField]
	private Camera depthCam;

	[SerializeField]
	private GameObject objectToAnimate;

	private string outputPath = "/Users/mmsamuel/Documents/Projects/MMLabs/highResolutionMLAnimation/CVAE/Data/UnityOutput/";

	private byte[][] allBytesArrays;

	private int index = 0;

	private Texture2D screenShot;

	private RenderTexture rt;

	private Rect imageRect;

	// Use this for initialization
	void Start () {

		StartCoroutine ("StartCamera");

	}
	
	IEnumerator StartCamera(){

		screenShot = new Texture2D(resWidth, resHeight, TextureFormat.RGB24, true);

		imageRect = new Rect(0, 0, resWidth, resHeight);

		allBytesArrays = new byte[numPics][];

		for(int i = 0; i<numPics; i++){

			objectToAnimate.transform.Rotate(0f,.1f,0f);

			if(canTakePictures){

				CreateImage(depthCam, screenShot,resWidth,resHeight, index);
				
				if(index%1000 == 0){
					Debug.Log(index);
				}
				index+=1;

			}
			yield return new WaitForEndOfFrame();

		}

		if(canTakePictures){
            SaveAllImages();
        }

		Debug.Log ("done");

		Debug.Log(Time.realtimeSinceStartup);

        #if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
        #endif

        #if UNITY_STANDALONE_OSX
            Application.Quit();
        #endif

	}

	void CreateImage(Camera camera, Texture2D screenShot, int width, int height, int index){

		rt = RenderTexture.GetTemporary(width, height, 24);
        
        camera.targetTexture = rt;
		camera.Render();
		RenderTexture.active = rt;
		screenShot.ReadPixels(imageRect, 0, 0, false);
		camera.targetTexture = null;
		RenderTexture.active = null; // JC: added to avoid errors

        RenderTexture.ReleaseTemporary(rt);

        allBytesArrays[index] = screenShot.EncodeToPNG();

	}

	void SaveAllImages(){

		string filename = "";
        for(int i = 0; i<allBytesArrays.Length;i++){
			filename = outputPath + "/" +  i.ToString("000000") + ".png";
            System.IO.File.WriteAllBytes(filename, allBytesArrays[i]);
        }
    }
	
}
