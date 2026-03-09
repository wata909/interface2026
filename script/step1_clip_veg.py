#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Step 1: 植生図を2次メッシュ境界でクリップして保存（ローカル実行）
=================================================================
veg2024bk3.gpkg は 700MB と大きいため conda 環境でローカル実行し、
研究範囲に切り抜いた軽量ファイルを出力する。
以降の連続性解析は notebook (step2_evaluate_connectivity.ipynb) で実施。

実行方法:
    conda run -n interface_forest python step1_local_veg.py

出力:
    veg_all_clipped.gpkg  研究範囲（2次メッシュ境界）でクリップした全植生
                          CRS: EPSG:6677, 面積フィールド area_m2 付き
"""

import os
import time

import geopandas as gpd

TARGET_MESHES = ['523956', '523957']


def load_target_mesh2(mesh2_path, target_meshes=None, output_crs='EPSG:4326'):
    target_meshes = target_meshes or TARGET_MESHES
    mesh2 = gpd.read_file(mesh2_path)
    return mesh2[mesh2['NAME'].isin(target_meshes)].to_crs(output_crs).copy()


def clip_vegetation_to_meshes(veg_path, mesh2_path, target_meshes=None, projected_crs='EPSG:6677'):
    target_mesh2 = load_target_mesh2(mesh2_path, target_meshes, output_crs='EPSG:4326')
    veg_bbox = gpd.read_file(veg_path, bbox=tuple(target_mesh2.total_bounds))
    aoi = target_mesh2.dissolve().to_crs(veg_bbox.crs)
    veg_clipped = gpd.clip(veg_bbox, aoi)
    veg_proj = veg_clipped.to_crs(projected_crs)
    veg_proj['area_m2'] = veg_proj.geometry.area
    return target_mesh2, veg_bbox, veg_clipped, veg_proj


# ----------------------------------------------------------------
# パス設定
# ----------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESH2_GPKG = os.path.join(BASE_DIR, 'mesh2.gpkg')
VEG_GPKG = os.path.join(BASE_DIR, 'veg2024bk3.gpkg')

OUT_ALL = os.path.join(BASE_DIR, 'veg_all_clipped.gpkg')


def main():
    print('=' * 60)
    print('Step 1: 植生図クリップ（ローカル実行）')
    print('=' * 60)

    print('\n[1] 2次メッシュを読み込み中...')
    t0 = time.time()
    target_mesh2, veg_bbox, veg_clipped, veg_proj = clip_vegetation_to_meshes(VEG_GPKG, MESH2_GPKG)
    print(f"  対象2次メッシュ: {list(target_mesh2['NAME'])}")

    print('\n[2] 植生図を読み込み中（bbox フィルタ）...')
    print(f'  bbox 読み込み完了: {len(veg_bbox):,} 件  ({time.time()-t0:.1f} 秒)')
    print(f'  CRS: {veg_bbox.crs}')
    print('  2次メッシュ境界でクリップ中...')
    print(f'  クリップ後: {len(veg_clipped):,} 件')

    print('\n[3] EPSG:6677 に変換・保存中...')
    veg_proj.to_file(OUT_ALL, driver='GPKG')
    print(f'  保存完了 -> {OUT_ALL}')
    print(f"  フィーチャ数: {len(veg_proj):,}  総面積: {veg_proj['area_m2'].sum()/1e6:.1f} km²")

    print(f'\n✓ Step 1 完了！  所要時間: {time.time()-t0:.1f} 秒')
    print('  次のステップ: step2_evaluate_connectivity.ipynb をノートブックで実行')


if __name__ == '__main__':
    main()
