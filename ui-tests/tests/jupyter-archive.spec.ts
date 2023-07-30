import { expect, galata, test } from '@jupyterlab/galata';
import * as path from 'path';

const fileName = 'folder.tar.xz';

test('should download a folder as an archive', async ({ page }) => {
  await page.locator('.jp-DirListing-content').click({
    button: 'right'
  });
  await page.getByText('New Folder').click();
  await page.keyboard.press('Enter');
  await page.getByRole('listitem', { name: 'Untitled Folder' }).click({
    button: 'right'
  });

  const downloadPromise = page.waitForEvent('download');
  await page.getByText('Download as an Archive').click();
  const download = await downloadPromise;
  expect(await download.path()).toBeDefined();
});

test('should download the current folder as an archive', async ({ page }) => {
  await page.locator('.jp-DirListing-content').click({
    button: 'right'
  });
  await page.getByText('New Folder').click();
  await page.keyboard.press('Enter');
  await page.getByRole('listitem', { name: 'Untitled Folder' }).click({
    button: 'right'
  });
  const downloadPromise = page.waitForEvent('download');
  await page.getByText('Download Current Folder as an Archive').click();
  const download = await downloadPromise;

  expect(await download.path()).toBeDefined();
});

test('should extract an archive', async ({ page, tmpPath }) => {
  const contents = galata.newContentsHelper(page.request);
  await contents.uploadFile(
    path.resolve(__dirname, `./data/${fileName}`),
    `${tmpPath}/${fileName}`
  );

  await page.getByRole('listitem', { name: 'folder.tar.xz' }).click({
    button: 'right'
  });
  await page.getByText('Extract Archive').click();
  await page.getByText('folder', { exact: true }).click();
});

test.describe('submenu', () => {
  test.use({
    mockSettings: {
      '@hadim/jupyter-archive:archive': {
        format: ''
      }
    }
  });

  test('should pick folder archive type from submenu', async ({ page }) => {
    await page.locator('.jp-DirListing-content').click({
      button: 'right'
    });
    await page.getByText('New Folder').click();
    await page.keyboard.press('Enter');
    await page.getByRole('listitem', { name: 'Untitled Folder' }).click({
      button: 'right'
    });

    await page.getByText('Download As').click();
    await expect(page.getByText('Archive')).toHaveCount(4);
  });
});
