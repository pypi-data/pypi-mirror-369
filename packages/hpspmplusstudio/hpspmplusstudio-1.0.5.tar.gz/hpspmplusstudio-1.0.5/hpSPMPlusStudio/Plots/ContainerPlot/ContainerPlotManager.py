import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from hpSPMPlusStudio.Container.NmiFrame.frame import NMIFrame
from hpSPMPlusStudio.Container.NmiImage.image import NMIImage
from hpSPMPlusStudio.Container.NmiContainer import NMIContainer


class ContainerPlotManager():
    def __init__(self):
        pass
    
    def plot16BitColorMapAllChannel(self, container: NMIContainer):
        num_images = len(container.ImageList)
        cols = int(np.ceil(np.sqrt(num_images)))
        rows = int(np.ceil(num_images / cols))
        
        fig, axes = plt.subplots(rows, cols, figsize=(8, 8))
        axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration
        
        for i, image in enumerate(container.ImageList):
            ax = axes[i]
            cax = ax.imshow(
                image.GetFirstFrame().Get16BitImageData(),  # 16-bit veriyi alıyoruz
                cmap='afmhot',
                interpolation='nearest',
                vmin=0,       # 16-bit için minimum değer
                vmax=65535    # 16-bit için maksimum değer
            )
            ax.axis('off')  # Eksenleri kaldırmak isterseniz
            
            # Başlık ve eksen etiketlerini ayarla
            frame_channel_title = image.GetFirstFrame().channel.name
            ax.set_title(f"Frame Channel: {frame_channel_title}")
            
            real_width = image.RealWidth
            real_height = image.RealHeight
            ax.set_xlabel(f"Width: {real_width} {image.RealWidthUnitPrefix}{image.RealWidthUnit}")
            ax.set_ylabel(f"Height: {real_height} {image.RealHeightUnitPrefix}{image.RealHeightUnit}")
            
            # Colorbar'ı aynı 'mappable' (cax) üzerinden oluştur
            cbar = fig.colorbar(cax, ax=ax, orientation='vertical')
            cbar.set_label('Intensity')
        
        # Remove any unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        
        plt.tight_layout()
        plt.show()   


    def plot8BitColorMapFromFrame(self, frame: NMIFrame):
        # Colormap uygulama
        colormap = plt.get_cmap('afmhot')
        colored_image_data = colormap(frame.Get8BitImageData())
        print(colored_image_data)
        plt.imshow(colored_image_data, interpolation='nearest')
        plt.axis('off')  # İstenirse eksenleri kaldırmak için
        plt.show()

    def _plot8BitColorMapFromImage(self, image: NMIImage):
        # Colormap uygulama
        colormap = plt.get_cmap('afmhot')
        colored_image_data = colormap(image.GetFirstFrame().Get8BitImageData())
        print(colored_image_data)
        
        fig, ax = plt.subplots()
        cax = ax.imshow(colored_image_data, interpolation='nearest')
        ax.axis('off')  # İstenirse eksenleri kaldırmak için
        
        # Frame channel title
        frame_channel_title = image.GetFirstFrame().channel.name
        plt.title(f"Frame Channel: {frame_channel_title}")
        
        # Real width and height
        real_width = image.RealHeight
        real_height = image.RealWidth
        plt.xlabel(f"Width: {real_width} {image.RealWidthUnitPrefix}{image.RealWidthUnit}")
        plt.ylabel(f"Height: {real_height}{image.RealHeightUnitPrefix}{image.RealHeightUnit}")
        
        # Color palette
        cbar = fig.colorbar(cax, ax=ax, orientation='vertical')
        cbar.set_label('Intensity')
        
        plt.show()

    def plot8BitColorMapFromImage(self, image:NMIImage):
        # 1. Şekil ve eksen oluştur
        fig, ax = plt.subplots()
        
        # 2. Görüntüyü afmhot colormap ile göster
        cax = ax.imshow(
            image.GetFirstFrame().Get8BitImageData(), 
            cmap='afmhot', 
            interpolation='nearest',
            vmin=0,       # 8-bit için genelde 0
            vmax=255      # 8-bit için genelde 255
        )
        ax.axis('off')  # Eksenleri kaldırmak isterseniz
        
        # 3. Başlık ve eksen etiketlerini ayarla
        frame_channel_title = image.GetFirstFrame().channel.name
        ax.set_title(f"Frame Channel: {frame_channel_title}")
        
        real_width = image.RealWidth
        real_height = image.RealHeight
        ax.set_xlabel(f"Width: {real_width} {image.RealWidthUnitPrefix}{image.RealWidthUnit}")
        ax.set_ylabel(f"Height: {real_height} {image.RealHeightUnitPrefix}{image.RealHeightUnit}")
        
        # 4. Colorbar'ı aynı 'mappable' (cax) üzerinden oluştur
        cbar = fig.colorbar(cax, ax=ax, orientation='vertical')
        cbar.set_label('Intensity')
        
        # 5. Göster
        plt.show()

    def plot16BitRawMapFromImage(self, image: NMIImage): 
        fig, ax = plt.subplots()
        data = image.GetFirstFrame().GetRawImageData()
        # 2. Görüntüyü afmhot colormap ile göster
        cax = ax.imshow(
            data,  # 16-bit veriyi alıyoruz
            cmap='afmhot',
            interpolation='nearest',
            vmin=0,       # 16-bit için minimum değer
            vmax=np.max(data)   # 16-bit için maksimum değer
        )
        ax.axis('off')  # Eksenleri kaldırmak isterseniz
        
        # 3. Başlık ve eksen etiketlerini ayarla
        frame_channel_title = image.GetFirstFrame().channel.name
        ax.set_title(f"Frame Channel: {frame_channel_title}")
        
        real_width = image.RealWidth
        real_height = image.RealHeight
        ax.set_xlabel(f"Width: {real_width} {image.RealWidthUnitPrefix}{image.RealWidthUnit}")
        ax.set_ylabel(f"Height: {real_height} {image.RealHeightUnitPrefix}{image.RealHeightUnit}")
        
        # 4. Colorbar'ı aynı 'mappable' (cax) üzerinden oluştur
        cbar = fig.colorbar(cax, ax=ax, orientation='vertical')
        cbar.set_label('Intensity')
        
        # 5. Göster
        plt.show()

    def plot16BitColorMapFromImage(self, image: NMIImage): 
        fig, ax = plt.subplots()
        
        # 2. Görüntüyü afmhot colormap ile göster
        cax = ax.imshow(
            image.GetFirstFrame().Get16BitImageData(),  # 16-bit veriyi alıyoruz
            cmap='afmhot',
            interpolation='nearest',
            vmin=0,       # 16-bit için minimum değer
            vmax=65535    # 16-bit için maksimum değer
        )
        ax.axis('off')  # Eksenleri kaldırmak isterseniz
        
        # 3. Başlık ve eksen etiketlerini ayarla
        frame_channel_title = image.GetFirstFrame().channel.name
        ax.set_title(f"Frame Channel: {frame_channel_title}")
        
        real_width = image.RealWidth
        real_height = image.RealHeight
        ax.set_xlabel(f"Width: {real_width} {image.RealWidthUnitPrefix}{image.RealWidthUnit}")
        ax.set_ylabel(f"Height: {real_height} {image.RealHeightUnitPrefix}{image.RealHeightUnit}")
        
        # 4. Colorbar'ı aynı 'mappable' (cax) üzerinden oluştur
        cbar = fig.colorbar(cax, ax=ax, orientation='vertical')
        cbar.set_label('Intensity')
        
        # 5. Göster
        plt.show()